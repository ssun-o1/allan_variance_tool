"""
艾伦方差分析工具 - GUI 版本
支持 Mac 和 Windows
"""
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from datetime import datetime
import platform
import threading

import time
import numpy as np
import pandas as pd
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart.marker import Marker
from openpyxl.chart.axis import Scaling
from openpyxl.drawing.image import Image as XLImage
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，用于打包
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, LogLocator, NullFormatter

TAU_STEP = 3.0

TIME_FORMATS = ("%Y-%m-%d %H:%M:%S",)

SERIES_COLORS = {"CO2": "000000", "CH4": "FF0000"}
MPL_COLORS = {"CO2": "black", "CH4": "red"}
AXIS_LABELS = {
    "CO2": "CO₂艾伦偏差 (ppm)",
    "CH4": "CH₄艾伦偏差 (ppb)",
}

plt.rcParams["font.sans-serif"] = [
    "PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS",
    "Microsoft YaHei", "SimHei", "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


def get_desktop_path():
    """获取桌面路径，兼容 Mac 和 Windows"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Desktop"
    elif system == "Windows":
        return Path.home() / "Desktop"
    else:  # Linux 或其他
        return Path.home() / "Desktop"


def parse_time_str(series):
    series = series.astype(str).str.strip()
    sample = series[series != ""].iloc[0] if (series != "").any() else ""
    formats = list(TIME_FORMATS)
    if sample:
        for fmt in TIME_FORMATS:
            try:
                datetime.strptime(sample, fmt)
                formats = [fmt] + [f for f in TIME_FORMATS if f != fmt]
                break
            except ValueError:
                continue

    last_err = None
    for fmt in formats:
        try:
            return pd.to_datetime(series, format=fmt)
        except (ValueError, TypeError) as exc:
            last_err = exc

    parsed = pd.to_datetime(series, errors="coerce")
    if parsed.isna().any():
        bad = series[parsed.isna()].iloc[0]
        raise ValueError(f"无法解析时间戳: {bad}") from last_err
    return parsed


def load_raw(path):
    path = Path(path)
    if not path.exists():
        return None

    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=["time_str", "conc_raw"],
        engine="python",
    )
    df["time_str"] = df["time_str"].str.strip()
    df["浓度"] = df["conc_raw"].astype(str).str.strip().astype(float)
    df["时间戳"] = parse_time_str(df["time_str"])
    df = df.drop(columns=["conc_raw"])
    return df


def compute_allan(df, gas_name):
    n = len(df)
    if n < 2:
        return None

    t_first = df["时间戳"].iloc[0]
    t_last = df["时间戳"].iloc[-1]
    total_seconds = (t_last - t_first).total_seconds()
    if total_seconds <= 0:
        return None

    actual_elapsed = (df["时间戳"] - t_first).dt.total_seconds().to_numpy(dtype=float)
    unique_elapsed = np.unique(actual_elapsed)
    if unique_elapsed.size == n and np.all(np.diff(actual_elapsed) > 0):
        elapsed_seconds = actual_elapsed
        tau0 = total_seconds / (n - 1)
    else:
        tau0 = total_seconds / (n - 1)
        elapsed_seconds = np.arange(n) * tau0

    raw_df = df.copy()
    raw_df["序号"] = np.arange(1, n + 1)
    raw_df["估计采样时刻"] = t_first + pd.to_timedelta(elapsed_seconds, unit="s")
    raw_df["累计时间(s)"] = elapsed_seconds
    raw_df["浓度"] = df["浓度"]
    raw_df = raw_df[["序号", "时间戳", "估计采样时刻", "累计时间(s)", "浓度"]]

    y = raw_df["浓度"].to_numpy(dtype=float)
    mean_y = y.mean()

    phi = np.zeros(n + 1, dtype=float)
    np.cumsum(y * tau0, out=phi[1:])

    m_step = TAU_STEP / tau0
    if m_step < 1:
        return None

    max_m = n // 4
    m_values = np.arange(m_step, max_m + 1, m_step)
    m_values = np.unique(np.round(m_values).astype(int))
    m_values = m_values[(m_values >= 1) & (m_values <= max_m)]

    rows = []
    for m in m_values:
        tau = m * tau0
        num_clusters = n - 2 * m
        if num_clusters < 5:
            continue
        diff2 = (
            phi[2 * m: 2 * m + num_clusters]
            - 2 * phi[m: m + num_clusters]
            + phi[:num_clusters]
        )
        avar = np.sum(diff2 ** 2) / (2.0 * num_clusters * tau ** 2)
        adev = np.sqrt(avar)
        rows.append({
            "平均因子m": int(m),
            "时间(s)": tau,
            "参与统计的簇数": int(num_clusters),
            "Allan方差": avar,
            "Allan偏差": adev,
            "相对Allan偏差": adev / mean_y if mean_y != 0 else np.nan,
        })

    allan_df = pd.DataFrame(rows)
    if allan_df.empty:
        return None

    info_df = pd.DataFrame({
        "项目": [
            "气体", "样本总数", "起始时间", "结束时间", "总时长(s)",
            "推算采样间隔tau0(s)", "tau间隔(s)", "浓度均值", "浓度标准差",
        ],
        "值": [
            gas_name, n, str(t_first), str(t_last), total_seconds,
            tau0, TAU_STEP, mean_y, y.std(ddof=1),
        ],
    })

    return {
        "gas": gas_name,
        "raw": raw_df,
        "info": info_df,
        "allan": allan_df,
    }


def process_gas(path, gas_name):
    try:
        if not path or path == "":
            return None
        df = load_raw(path)
        if df is None:
            return None
        return compute_allan(df, gas_name)
    except Exception as exc:
        print(f"[{gas_name}] 处理失败: {exc}")
        return None


def _plain_tick(x, _pos=None):
    if x == 0:
        return "0"
    abs_x = abs(x)
    if abs_x >= 1 and abs(x - round(x)) < 1e-9 * max(abs_x, 1.0):
        return str(int(round(x)))
    if abs_x >= 1:
        text = f"{x:.4f}".rstrip("0").rstrip(".")
    elif abs_x >= 0.01:
        text = f"{x:.2f}"
    else:
        text = f"{x:.6f}".rstrip("0").rstrip(".")
    return text if text not in ("", "-") else "0"


def _nice_ylim(vmax):
    if vmax <= 0:
        return 1.0
    exp = int(np.floor(np.log10(vmax)))
    step = 10.0 ** exp
    top = np.ceil(vmax / step) * step
    if top / vmax > 1.6:
        half = step / 2.0
        top = np.ceil(vmax / half) * half
    return float(top)


def _apply_plain_y_axis(ax, values):
    vmax = float(np.nanmax(values)) if len(values) else 0.0
    top = _nice_ylim(vmax)
    ax.set_ylim(0, top)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:.3f}"))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))


def plot_allan_figure(results, png_path):
    by_gas = {r["gas"]: r["allan"] for r in results}
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_xscale("log")
    ax.set_xlabel("时间 (s)", fontsize=12)
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(FuncFormatter(_plain_tick))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.grid(False)

    all_tau = np.concatenate([df["时间(s)"].to_numpy() for df in by_gas.values()])
    tmin, tmax = float(np.nanmin(all_tau)), float(np.nanmax(all_tau))
    ax.set_xlim(max(tmin * 0.7, 1e-6), tmax * 1.15)

    ax2 = None
    has_co2 = "CO2" in by_gas
    has_ch4 = "CH4" in by_gas

    if has_co2:
        df = by_gas["CO2"]
        ax.plot(
            df["时间(s)"], df["Allan偏差"],
            color=MPL_COLORS["CO2"], linewidth=1.3,
            solid_capstyle="round", solid_joinstyle="round",
        )
        ax.set_ylabel(AXIS_LABELS["CO2"], color=MPL_COLORS["CO2"], fontsize=12)
        ax.tick_params(axis="y", colors=MPL_COLORS["CO2"])
        ax.spines["left"].set_color(MPL_COLORS["CO2"])
        _apply_plain_y_axis(ax, df["Allan偏差"].to_numpy())
    elif has_ch4:
        df = by_gas["CH4"]
        ax.plot(
            df["时间(s)"], df["Allan偏差"],
            color=MPL_COLORS["CH4"], linewidth=1.3,
            solid_capstyle="round", solid_joinstyle="round",
        )
        ax.set_ylabel(AXIS_LABELS["CH4"], color=MPL_COLORS["CH4"], fontsize=12)
        ax.tick_params(axis="y", colors=MPL_COLORS["CH4"])
        ax.spines["left"].set_color(MPL_COLORS["CH4"])
        _apply_plain_y_axis(ax, df["Allan偏差"].to_numpy())

    if has_co2 and has_ch4:
        df = by_gas["CH4"]
        ax2 = ax.twinx()
        ax2.plot(
            df["时间(s)"], df["Allan偏差"],
            color=MPL_COLORS["CH4"], linewidth=1.3,
            solid_capstyle="round", solid_joinstyle="round",
        )
        ax2.set_ylabel(AXIS_LABELS["CH4"], color=MPL_COLORS["CH4"], fontsize=12)
        ax2.tick_params(axis="y", colors=MPL_COLORS["CH4"])
        ax2.spines["right"].set_color(MPL_COLORS["CH4"])
        ax2.spines["left"].set_visible(False)
        ax2.spines["top"].set_color("black")
        ax2.spines["bottom"].set_visible(False)
        _apply_plain_y_axis(ax2, df["Allan偏差"].to_numpy())

    ax.tick_params(which="both", direction="in", top=True, labelsize=10)
    for spine in ("top", "bottom", "left", "right"):
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(1.0)
    ax.spines["top"].set_color("black")
    ax.spines["bottom"].set_color("black")

    if ax2 is None:
        ax.tick_params(which="both", direction="in", right=True)
        ax.spines["right"].set_color("black")
    else:
        ax.spines["right"].set_visible(False)
        ax2.tick_params(which="both", direction="in", labelsize=10)
        ax2.spines["right"].set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(png_path, dpi=180, facecolor="white")
    plt.close(fig)
    return png_path


def write_excel(results, dst):
    png_path = Path(str(dst).rsplit(".", 1)[0] + "_图表.png")

    with pd.ExcelWriter(dst, engine="openpyxl") as writer:
        for result in results:
            gas = result["gas"]
            result["raw"].to_excel(writer, sheet_name=f"{gas}_原始数据", index=False)

            info_df = result["info"]
            allan_df = result["allan"]
            sheet_name = f"{gas}_艾伦偏差结果"
            info_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)

            start_row = len(info_df) + 3
            allan_df.to_excel(
                writer, sheet_name=sheet_name, index=False, startrow=start_row
            )

        plot_allan_figure(results, png_path)
        chart_ws = writer.book.create_sheet("图表")
        chart_ws["A1"] = "CO2 / CH4 艾伦偏差折线图"
        img = XLImage(str(png_path))
        img.anchor = "A3"
        chart_ws.add_image(img)

    return png_path


class AllanVarianceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("艾伦方差分析工具")
        self.root.geometry("700x650")
        self.root.resizable(False, False)

        # 配色方案 - 浅色主题，清新专业风格
        self.colors = {
            'bg_primary': '#FFFFFF',      # 主背景 - 白色
            'bg_secondary': '#F8FAFC',    # 次级背景 - 浅灰
            'bg_card': '#FFFFFF',         # 卡片背景
            'accent': '#38BDF8',          # 强调色 - 青蓝
            'accent_hover': '#0EA5E9',    # 悬停色
            'text_primary': '#0F172A',    # 主文字 - 深色
            'text_secondary': '#475569',  # 次要文字
            'text_muted': '#94A3B8',      # 弱化文字
            'border': '#E2E8F0',          # 边框 - 浅灰
            'success': '#10B981',         # 成功色 - 绿色
            'error': '#EF4444',           # 错误色 - 红色
            'co2_color': '#10B981',       # CO2 - 绿色
            'co2_hover': '#059669',       # CO2 悬停
            'ch4_color': '#EF4444',       # CH4 - 红色
            'ch4_hover': '#DC2626',       # CH4 悬停
        }

        # 文件路径变量
        self.co2_path = tk.StringVar()
        self.ch4_path = tk.StringVar()

        # 按钮引用
        self.co2_btn = None
        self.ch4_btn = None

        # 进度追踪
        self.current_step = 0
        self.total_steps = 0
        self.step_names = []

        # Loading 动画
        self.loading_canvas = None
        self.loading_angle = 0
        self.loading_animation_id = None

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """配置 ttk 样式"""
        style = ttk.Style()

        # 进度条样式
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.colors['bg_secondary'],
            background=self.colors['accent'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['accent'],
            darkcolor=self.colors['accent']
        )

    def create_widgets(self):
        # 设置主窗口背景
        self.root.configure(bg=self.colors['bg_primary'])

        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # 标题区域
        title_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 30))

        title = tk.Label(
            title_frame,
            text="艾伦方差分析工具",
            font=("PingFang SC", 24, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="Allan Variance Analysis Tool",
            font=("Arial", 11),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary']
        )
        subtitle.pack(pady=(5, 0))

        # 文件选择区域 - CO2
        self.co2_btn = self.create_file_selector(
            main_container,
            "CO2 数据文件",
            "二氧化碳浓度数据",
            self.co2_path,
            self.select_co2,
            self.colors['co2_color'],
            self.colors['co2_hover']
        )

        # 文件选择区域 - CH4
        self.ch4_btn = self.create_file_selector(
            main_container,
            "CH4 数据文件",
            "甲烷浓度数据",
            self.ch4_path,
            self.select_ch4,
            self.colors['ch4_color'],
            self.colors['ch4_hover']
        )

        # 说明卡片
        info_card = tk.Frame(
            main_container,
            bg=self.colors['bg_card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        info_card.pack(fill=tk.X, pady=(20, 0))

        info_inner = tk.Frame(info_card, bg=self.colors['bg_card'])
        info_inner.pack(padx=20, pady=15)

        info_title = tk.Label(
            info_inner,
            text="📋 使用说明",
            font=("PingFang SC", 12, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            anchor="w"
        )
        info_title.pack(anchor="w", pady=(0, 10))

        info_items = [
            "• 至少选择一个气体的数据文件（CO2 或 CH4）",
            "• 数据格式：制表符分隔的两列（时间戳 \\t 浓度值）",
            "• 支持时间格式：YYYY-MM-DD HH:MM:SS",
            "• 分析结果将自动保存到桌面（Excel + 图表）"
        ]

        for item in info_items:
            item_label = tk.Label(
                info_inner,
                text=item,
                font=("PingFang SC", 10),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                anchor="w",
                justify=tk.LEFT
            )
            item_label.pack(anchor="w", pady=2)

        # 开始分析按钮
        btn_container = tk.Frame(main_container, bg=self.colors['bg_primary'])
        btn_container.pack(pady=(25, 0))

        self.start_btn = tk.Button(
            btn_container,
            text="开始分析",
            command=self.start_analysis,
            bg=self.colors['accent'],
            fg='white',
            font=("PingFang SC", 13, "bold"),
            activebackground=self.colors['accent_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor="hand2",
            padx=40,
            pady=12,
            borderwidth=0
        )
        self.start_btn.pack()

        # 添加按钮悬停效果
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg=self.colors['accent_hover']))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg=self.colors['accent']))

        # 进度区域
        self.progress_container = tk.Frame(main_container, bg=self.colors['bg_primary'])

        # Loading 动画 Canvas
        self.loading_canvas = tk.Canvas(
            self.progress_container,
            width=80,
            height=80,
            bg=self.colors['bg_primary'],
            highlightthickness=0
        )
        self.loading_canvas.pack(pady=(0, 15))

        # 进度文本
        self.progress_text = tk.Label(
            self.progress_container,
            text="",
            font=("PingFang SC", 12, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['accent']
        )
        self.progress_text.pack(pady=(0, 5))

        # 状态标签
        self.status_label = tk.Label(
            main_container,
            text="",
            font=("PingFang SC", 10),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            wraplength=640,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=(10, 0))

    def create_file_selector(self, parent, label_text, description, var, command, color, hover_color):
        """创建文件选择器组件"""
        card = tk.Frame(
            parent,
            bg=self.colors['bg_card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(padx=20, pady=15, fill=tk.X)

        # 标题行
        title_row = tk.Frame(inner, bg=self.colors['bg_card'])
        title_row.pack(fill=tk.X, pady=(0, 8))

        # 颜色指示器
        indicator = tk.Frame(
            title_row,
            bg=color,
            width=4,
            height=16
        )
        indicator.pack(side=tk.LEFT, padx=(0, 8))

        label = tk.Label(
            title_row,
            text=label_text,
            font=("PingFang SC", 12, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            anchor="w"
        )
        label.pack(side=tk.LEFT)

        desc = tk.Label(
            title_row,
            text=description,
            font=("PingFang SC", 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text_muted'],
            anchor="w"
        )
        desc.pack(side=tk.LEFT, padx=(8, 0))

        # 文件路径行
        path_row = tk.Frame(inner, bg=self.colors['bg_card'])
        path_row.pack(fill=tk.X)

        entry = tk.Entry(
            path_row,
            textvariable=var,
            font=("Monaco", 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent']
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))

        btn = tk.Button(
            path_row,
            text="选择文件",
            command=command,
            bg=color,
            fg="white",
            font=("PingFang SC", 10, "bold"),
            activebackground=hover_color,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=6,
            borderwidth=0
        )
        btn.pack(side=tk.LEFT)

        # 按钮悬停效果
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color) if btn['state'] == 'normal' else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=color) if btn['state'] == 'normal' else None)

        return btn

    def select_co2(self):
        filename = filedialog.askopenfilename(
            title="选择 CO2 数据文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.co2_path.set(filename)
            # 禁用按钮
            self.co2_btn.config(
                state=tk.DISABLED,
                bg=self.colors['text_muted'],
                cursor="arrow",
                text="已选择"
            )

    def select_ch4(self):
        filename = filedialog.askopenfilename(
            title="选择 CH4 数据文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.ch4_path.set(filename)
            # 禁用按钮
            self.ch4_btn.config(
                state=tk.DISABLED,
                bg=self.colors['text_muted'],
                cursor="arrow",
                text="已选择"
            )

    def start_analysis(self):
        co2_file = self.co2_path.get()
        ch4_file = self.ch4_path.get()

        if not co2_file and not ch4_file:
            self.show_warning("请至少选择一个气体的数据文件")
            return

        # 计算总步骤数
        self.step_names = []
        if co2_file:
            self.step_names.append("读取 CO2 数据")
            self.step_names.append("计算 CO2 艾伦方差")
        if ch4_file:
            self.step_names.append("读取 CH4 数据")
            self.step_names.append("计算 CH4 艾伦方差")
        self.step_names.extend(["生成图表", "写入 Excel 文件"])

        self.total_steps = len(self.step_names)
        self.current_step = 0

        # 禁用按钮，显示进度区域
        self.start_btn.config(state=tk.DISABLED, bg=self.colors['border'])
        self.progress_container.pack(pady=(20, 0))
        self.start_loading_animation()

        # 在新线程中执行分析
        thread = threading.Thread(
            target=self.run_analysis,
            args=(co2_file, ch4_file),
            daemon=True
        )
        thread.start()

    def start_loading_animation(self):
        """启动 loading 动画"""
        self.loading_angle = 0
        self.animate_loading()

    def animate_loading(self):
        """绘制旋转的 loading 动画"""
        if self.loading_canvas is None:
            return

        self.loading_canvas.delete("all")

        # 绘制多个旋转的圆点
        center_x, center_y = 40, 40
        radius = 25
        num_dots = 8

        for i in range(num_dots):
            angle = (self.loading_angle + i * 360 / num_dots) % 360
            radian = angle * 3.14159 / 180

            x = center_x + radius * np.cos(radian)
            y = center_y + radius * np.sin(radian)

            # 根据位置计算透明度（通过颜色深浅模拟）
            opacity = 1.0 - (i / num_dots) * 0.7

            # 使用不同大小和颜色深浅
            dot_size = 4 + 2 * opacity

            # 将 RGB 颜色转换为 hex
            color_value = int(56 + (255 - 56) * (1 - opacity))  # 从浅到深
            color = f'#{color_value:02x}{189 + int((255 - 189) * (1 - opacity)):02x}{248:02x}'

            self.loading_canvas.create_oval(
                x - dot_size, y - dot_size,
                x + dot_size, y + dot_size,
                fill=color,
                outline=""
            )

        self.loading_angle = (self.loading_angle + 15) % 360
        self.loading_animation_id = self.root.after(50, self.animate_loading)

    def stop_loading_animation(self):
        """停止 loading 动画"""
        if self.loading_animation_id is not None:
            self.root.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
        if self.loading_canvas is not None:
            self.loading_canvas.delete("all")

    def run_analysis(self, co2_file, ch4_file):
        try:
            results = []

            # 处理 CO2
            if co2_file:
                self.update_progress("读取 CO2 数据文件...")
                df_co2 = load_raw(co2_file)
                if df_co2 is None:
                    self.show_error("无法读取 CO2 数据文件")
                    return

                self.update_progress("计算 CO2 艾伦方差...")
                result = compute_allan(df_co2, "CO2")
                if result:
                    results.append(result)

            # 处理 CH4
            if ch4_file:
                self.update_progress("读取 CH4 数据文件...")
                df_ch4 = load_raw(ch4_file)
                if df_ch4 is None:
                    self.show_error("无法读取 CH4 数据文件")
                    return

                self.update_progress("计算 CH4 艾伦方差...")
                result = compute_allan(df_ch4, "CH4")
                if result:
                    results.append(result)

            if not results:
                self.show_error("没有成功处理的数据，请检查文件格式")
                return

            # 生成输出文件
            self.update_progress("生成分析图表...")
            desktop = get_desktop_path()
            timestamp = int(time.time())
            output_file = desktop / f"艾伦方差分析结果_{timestamp}.xlsx"

            self.update_progress("写入 Excel 文件...")
            png_path = write_excel(results, output_file)

            self.show_success(f"分析完成！\n\n结果已保存到桌面:\n{output_file.name}")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"错误详情:\n{error_detail}")
            self.show_error(f"处理过程中出错:\n{str(e)}")
        finally:
            self.reset_ui()

    def update_progress(self, message):
        """更新进度和状态文本"""
        self.current_step += 1

        def update():
            self.progress_text.config(
                text=f"步骤 {self.current_step}/{self.total_steps}",
                fg=self.colors['accent']
            )
            self.status_label.config(
                text=message,
                fg=self.colors['text_secondary']
            )

        self.root.after(0, update)
        time.sleep(0.3)  # 让用户能看到进度变化

    def show_success(self, message):
        def show():
            self.stop_loading_animation()
            self.status_label.config(
                text="✓ " + message.split('\n')[0],
                fg=self.colors['success']
            )
            messagebox.showinfo("成功", message)
        self.root.after(0, show)

    def show_error(self, message):
        def show():
            self.stop_loading_animation()
            self.status_label.config(
                text="✗ " + message.split('\n')[0],
                fg=self.colors['error']
            )
            messagebox.showerror("错误", message)
        self.root.after(0, show)

    def show_warning(self, message):
        messagebox.showwarning("警告", message)

    def reset_ui(self):
        self.root.after(0, self._reset_ui_impl)

    def _reset_ui_impl(self):
        self.stop_loading_animation()
        self.progress_container.pack_forget()
        self.start_btn.config(state=tk.NORMAL, bg=self.colors['accent'])
        # 重新启用文件选择按钮
        if self.co2_path.get():
            self.co2_btn.config(
                state=tk.NORMAL,
                bg=self.colors['co2_color'],
                cursor="hand2",
                text="选择文件"
            )
        if self.ch4_path.get():
            self.ch4_btn.config(
                state=tk.NORMAL,
                bg=self.colors['ch4_color'],
                cursor="hand2",
                text="选择文件"
            )
        # 保留状态信息，不清空


def show_loading_window():
    """显示加载窗口"""
    loading_window = tk.Tk()
    loading_window.title("正在启动...")
    loading_window.overrideredirect(True)  # 无边框窗口

    # 窗口大小和位置
    window_width = 400
    window_height = 200
    screen_width = loading_window.winfo_screenwidth()
    screen_height = loading_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 设置背景
    loading_window.configure(bg='#0F131C')

    # 主容器
    container = tk.Frame(loading_window, bg='#0F131C')
    container.pack(expand=True)

    # 标题
    title = tk.Label(
        container,
        text="艾伦方差分析工具",
        font=("PingFang SC", 20, "bold"),
        bg='#0F131C',
        fg='#E8F5FE'
    )
    title.pack(pady=(20, 5))

    # 副标题
    subtitle = tk.Label(
        container,
        text="Allan Variance Analysis Tool",
        font=("Arial", 11),
        bg='#0F131C',
        fg='#38BDF8'
    )
    subtitle.pack(pady=(0, 30))

    # 加载提示
    loading_label = tk.Label(
        container,
        text="正在加载，请稍候...",
        font=("PingFang SC", 12),
        bg='#0F131C',
        fg='#6B7280'
    )
    loading_label.pack()

    # 进度动画
    progress_frame = tk.Frame(container, bg='#0F131C')
    progress_frame.pack(pady=(15, 0))

    dots = []
    for i in range(3):
        dot = tk.Label(
            progress_frame,
            text="●",
            font=("Arial", 16),
            bg='#0F131C',
            fg='#38BDF8'
        )
        dot.pack(side=tk.LEFT, padx=5)
        dots.append(dot)

    # 动画效果
    def animate_dots(index=0):
        for i, dot in enumerate(dots):
            if i == index:
                dot.config(fg='#38BDF8')
            else:
                dot.config(fg='#1E2636')
        loading_window.after(300, lambda: animate_dots((index + 1) % 3))

    animate_dots()

    loading_window.update()
    return loading_window


def main():
    # 显示加载窗口
    loading_window = show_loading_window()

    # 模拟加载时间，让用户看到加载画面
    loading_window.after(800, lambda: None)
    loading_window.update()

    # 创建主窗口
    root = tk.Tk()

    # 关闭加载窗口
    loading_window.destroy()

    # 启动应用
    app = AllanVarianceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
