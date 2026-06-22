"""Centralized elite cyber-tech theme for NeuralRadar.
Simple attribute-based COLORS for compatibility. Premium QSS for SOC dashboard.
"""
from PySide6.QtGui import QFont


class Colors:
    """Elite palette as attributes for easy .PRIMARY access."""
    # Layered dark backgrounds (darkest → lightest)
    BG_MAIN = "#050A14"
    SURFACE = "#0A1020"
    PANEL = "#0F1729"
    CARD = "#141E35"
    BG_CARD = CARD
    CARD_HOVER = "#1A2A48"
    BORDER = "#1E3050"
    BORDER_SUBTLE = "#162440"

    # Accent colors
    PRIMARY = "#00E5FF"        # Cyan — primary brand accent
    PRIMARY_DIM = "#00B8D4"    # Dimmer cyan for subtle accents
    NEURAL_BLUE = "#38BDF8"    # Light blue
    PURPLE = "#7C3AED"         # NeuralShield purple
    SECONDARY = "#7C3AED"

    # Semantic colors
    SUCCESS = "#22C55E"
    SUCCESS_DIM = "#16A34A"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"
    DANGER_DIM = "#DC2626"

    # Text
    TEXT = "#E2E8F0"
    TEXT_BRIGHT = "#F1F5F9"
    MUTED = "#8896B3"

    # Table
    TABLE_BG = "#0C1424"
    TABLE_ALT = "#111C32"
    TABLE_HEADER_BG = "#0A1428"
    TABLE_GRID = "#1A2844"
    TABLE_SELECTION = "rgba(0, 229, 255, 0.12)"


class Theme:
    """Central theme with reusable premium stylesheets."""
    COLORS = Colors()
    FONT_FAMILY = "Segoe UI, system-ui, sans-serif"
    TITLE_SIZE = "48px"
    HEADER_SIZE = "22px"
    BODY_SIZE = "13px"

    # ─── Global Stylesheet ────────────────────────────────────────────

    @classmethod
    def get_global_stylesheet(cls):
        c = cls.COLORS
        return f"""
            QMainWindow, QWidget {{
                background-color: {c.BG_MAIN};
                color: {c.TEXT};
                font-family: {cls.FONT_FAMILY};
                font-size: 13px;
            }}
            QFrame, QGroupBox {{
                background-color: {c.PANEL};
                border: 1px solid {c.BORDER};
                border-radius: 10px;
            }}
            .EliteCard {{
                background-color: {c.CARD};
                border: 1px solid {c.BORDER};
                border-radius: 12px;
            }}
            .EliteCard:hover {{
                background-color: {c.CARD_HOVER};
                border-color: {c.PRIMARY};
            }}

            QLabel#Header {{
                font-size: {cls.HEADER_SIZE};
                font-weight: 600;
                color: {c.PRIMARY};
            }}

            QPushButton {{
                background: {c.CARD};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {c.PRIMARY_DIM};
                background: {c.CARD_HOVER};
            }}
            QPushButton:disabled {{
                background: {c.PANEL};
                color: {c.MUTED};
                border-color: {c.BORDER_SUBTLE};
            }}
            QPushButton[primary="true"] {{
                background: {c.PRIMARY};
                color: #050A14;
                font-weight: 600;
                border: none;
            }}
            QPushButton[primary="true"]:hover {{
                background: #67f0ff;
            }}
            QPushButton[success="true"] {{
                background: {c.SUCCESS};
                color: #050A14;
                font-weight: 600;
            }}
            QPushButton[danger="true"] {{
                color: {c.DANGER};
                border: 1px solid {c.DANGER};
                background: transparent;
            }}
            QPushButton[danger="true"]:hover {{
                background: {c.DANGER};
                color: white;
            }}

            QLineEdit, QComboBox {{
                background: {c.SURFACE};
                border: 1px solid {c.BORDER};
                border-radius: 6px;
                padding: 10px;
                color: {c.TEXT};
                font-size: 13px;
                selection-background-color: rgba(0, 229, 255, 0.25);
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {c.PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c.PANEL};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                selection-background-color: {c.TABLE_SELECTION};
            }}

            QTextEdit {{
                background: {c.SURFACE};
                border: 1px solid {c.BORDER};
                border-radius: 6px;
                padding: 8px;
                color: {c.TEXT};
                font-size: 13px;
                selection-background-color: rgba(0, 229, 255, 0.25);
            }}
            QTextEdit:focus {{
                border-color: {c.PRIMARY};
            }}

            QTableWidget, QTableView {{
                background: {c.TABLE_BG};
                alternate-background-color: {c.TABLE_ALT};
                border: 1px solid {c.BORDER};
                border-radius: 8px;
                gridline-color: {c.TABLE_GRID};
                selection-background-color: {c.TABLE_SELECTION};
                outline: none;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                outline: none;
            }}
            QTableWidget::item:focus {{
                outline: none;
            }}
            QTableWidget::item:selected {{
                background-color: {c.TABLE_SELECTION};
                color: {c.TEXT_BRIGHT};
                outline: none;
            }}
            QHeaderView::section {{
                background: {c.TABLE_HEADER_BG};
                color: {c.PRIMARY_DIM};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {c.PRIMARY_DIM};
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QLabel[status="active"], QLabel[status="online"] {{
                background: rgba(34,197,94,0.12);
                color: {c.SUCCESS};
                border: 1px solid rgba(34,197,94,0.35);
                padding: 4px 14px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 500;
            }}
            QLabel[status="coming-soon"] {{
                background: rgba(136,150,179,0.1);
                color: {c.MUTED};
                border: 1px solid rgba(136,150,179,0.25);
                padding: 4px 14px;
                border-radius: 9999px;
                font-size: 12px;
            }}
            QLabel[status="warning"] {{
                background: rgba(245,158,11,0.12);
                color: {c.WARNING};
                border: 1px solid rgba(245,158,11,0.35);
                padding: 4px 14px;
                border-radius: 9999px;
            }}
            QLabel[status="error"] {{
                background: rgba(239,68,68,0.12);
                color: {c.DANGER};
                border: 1px solid rgba(239,68,68,0.35);
                padding: 4px 14px;
                border-radius: 9999px;
            }}

            .DetailsPanel {{
                background: {c.CARD};
                border: 1px solid {c.BORDER};
                border-radius: 12px;
                padding: 20px;
            }}

            QScrollBar:vertical {{
                background: {c.SURFACE};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {c.BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c.PRIMARY_DIM};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {c.SURFACE};
                height: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {c.BORDER};
                border-radius: 4px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {c.PRIMARY_DIM};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            QCheckBox {{
                color: {c.MUTED};
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c.BORDER};
                border-radius: 3px;
                background: {c.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background: {c.PRIMARY};
                border-color: {c.PRIMARY};
            }}

            QSplitter::handle {{
                background-color: transparent;
            }}
        """

    # ─── Card Style ───────────────────────────────────────────────────

    @classmethod
    def get_card_style(cls, is_active: bool = True, active: bool | None = None) -> str:
        """Supports both is_active= and active= for full backward compatibility."""
        if active is not None:
            is_active = active
        c = cls.COLORS
        border = c.PRIMARY_DIM if is_active else c.BORDER
        bg = c.CARD if is_active else "#0D1525"
        return f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {c.PRIMARY};
                background-color: {c.CARD_HOVER};
            }}
        """

    # ─── Sidebar Style ────────────────────────────────────────────────

    @classmethod
    def get_sidebar_style(cls):
        c = cls.COLORS
        return f"""
            QWidget#Sidebar {{
                background-color: {c.SURFACE};
                border-right: 1px solid {c.BORDER};
            }}
            QLabel#Logo {{
                color: {c.PRIMARY};
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            QLabel#Subtitle {{
                color: {c.PURPLE};
                font-size: 11px;
                font-weight: 500;
                letter-spacing: 1px;
            }}
            QLabel#VersionBadge {{
                background: rgba(124,58,237,0.12);
                color: {c.PURPLE};
                border: 1px solid rgba(124,58,237,0.3);
                border-radius: 9999px;
                padding: 4px 14px;
                font-size: 11px;
            }}
            QLabel#SectionLabel {{
                color: {c.MUTED};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 2px;
                padding: 16px 24px 6px 24px;
                border: none;
                background: transparent;
            }}
            QFrame#SidebarDivider {{
                background-color: {c.BORDER};
                border: none;
                max-height: 1px;
                min-height: 1px;
            }}
            QPushButton#navButton {{
                background: transparent;
                color: {c.MUTED};
                text-align: left;
                padding: 12px 24px;
                border-radius: 8px;
                margin: 2px 8px;
                font-size: 13px;
                font-weight: 500;
                border: none;
            }}
            QPushButton#navButton:hover {{
                background-color: rgba(0, 229, 255, 0.06);
                color: {c.TEXT};
            }}
            QPushButton#navButton:checked {{
                background-color: rgba(0, 229, 255, 0.1);
                color: {c.PRIMARY};
                border-left: 3px solid {c.PRIMARY};
            }}
            QLabel#StatusPill {{
                background: rgba(0,229,255,0.06);
                color: {c.MUTED};
                border: 1px solid rgba(0,229,255,0.2);
                border-radius: 9999px;
                padding: 8px;
                font-size: 10px;
                text-align: center;
            }}
        """

    # ─── Page Header ──────────────────────────────────────────────────

    @classmethod
    def page_title_style(cls):
        c = cls.COLORS
        return f"color: {c.TEXT_BRIGHT}; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;"

    @classmethod
    def page_subtitle_style(cls):
        c = cls.COLORS
        return f"color: {c.PRIMARY_DIM}; font-size: 14px; font-weight: 400;"

    # ─── Notice Bars ──────────────────────────────────────────────────

    @classmethod
    def notice_style(cls, variant="info"):
        c = cls.COLORS
        if variant == "warning":
            color = c.WARNING
            bg = "rgba(245, 158, 11, 0.08)"
            border = "rgba(245, 158, 11, 0.25)"
        elif variant == "danger":
            color = c.DANGER
            bg = "rgba(239, 68, 68, 0.08)"
            border = "rgba(239, 68, 68, 0.25)"
        else:  # info
            color = c.SUCCESS
            bg = "rgba(34, 197, 94, 0.08)"
            border = "rgba(34, 197, 94, 0.25)"
        return f"color: {color}; font-size: 13px; font-weight: 500; background-color: {bg}; padding: 10px 16px; border-radius: 8px; border: 1px solid {border};"

    # ─── Input Fields ─────────────────────────────────────────────────

    @classmethod
    def input_style(cls):
        c = cls.COLORS
        return f"""
            QLineEdit {{
                background-color: {c.SURFACE};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: rgba(0, 229, 255, 0.25);
            }}
            QLineEdit:focus {{
                border: 1px solid {c.PRIMARY};
            }}
        """

    @classmethod
    def combo_style(cls):
        c = cls.COLORS
        return f"""
            QComboBox {{
                background-color: {c.SURFACE};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 14px;
                min-width: 200px;
            }}
            QComboBox:focus {{
                border: 1px solid {c.PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c.PANEL};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                selection-background-color: {c.TABLE_SELECTION};
            }}
        """

    # ─── Buttons ──────────────────────────────────────────────────────

    @classmethod
    def primary_btn_style(cls):
        c = cls.COLORS
        return f"""
            QPushButton {{
                background-color: {c.PRIMARY};
                color: #050A14;
                font-weight: 600;
                padding: 10px 22px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #33ECFF;
            }}
            QPushButton:disabled {{
                background-color: {c.PANEL};
                color: {c.MUTED};
                border: 1px solid {c.BORDER_SUBTLE};
            }}
        """

    @classmethod
    def danger_btn_style(cls):
        c = cls.COLORS
        return f"""
            QPushButton {{
                background-color: {c.DANGER};
                color: #FFFFFF;
                font-weight: 600;
                padding: 10px 22px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #F87171;
            }}
            QPushButton:disabled {{
                background-color: {c.PANEL};
                color: {c.MUTED};
                border: 1px solid {c.BORDER_SUBTLE};
            }}
        """

    @classmethod
    def success_btn_style(cls):
        c = cls.COLORS
        return f"""
            QPushButton {{
                background-color: {c.SUCCESS};
                color: #050A14;
                font-weight: 600;
                padding: 10px 22px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #4ADE80;
            }}
            QPushButton:disabled {{
                background-color: {c.PANEL};
                color: {c.MUTED};
                border: 1px solid {c.BORDER_SUBTLE};
            }}
        """

    @classmethod
    def secondary_btn_style(cls):
        c = cls.COLORS
        return f"""
            QPushButton {{
                background-color: {c.CARD};
                color: {c.TEXT};
                font-weight: 500;
                padding: 8px 18px;
                border-radius: 6px;
                border: 1px solid {c.BORDER};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {c.PRIMARY_DIM};
                background-color: {c.CARD_HOVER};
                color: {c.PRIMARY};
            }}
            QPushButton:disabled {{
                background-color: {c.PANEL};
                color: {c.MUTED};
                border-color: {c.BORDER_SUBTLE};
            }}
        """

    # ─── Tables ───────────────────────────────────────────────────────

    @classmethod
    def table_style(cls):
        c = cls.COLORS
        return f"""
            QTableWidget {{
                background-color: {c.TABLE_BG};
                alternate-background-color: {c.TABLE_ALT};
                color: {c.TEXT};
                border: 1px solid {c.BORDER};
                border-radius: 8px;
                gridline-color: {c.TABLE_GRID};
                outline: none;
                font-size: 13px;
            }}
            QTableWidget:focus {{
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {c.TABLE_HEADER_BG};
                color: {c.PRIMARY_DIM};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {c.PRIMARY_DIM};
                font-weight: 600;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                outline: none;
            }}
            QTableWidget::item:focus {{
                outline: none;
            }}
            QTableWidget::item:selected {{
                background-color: {c.TABLE_SELECTION};
                color: {c.TEXT_BRIGHT};
                outline: none;
            }}
        """

    @classmethod
    def compact_table_style(cls):
        """For smaller embedded tables (services, web metadata)."""
        c = cls.COLORS
        return f"""
            QTableWidget {{
                background-color: {c.TABLE_BG};
                alternate-background-color: {c.TABLE_ALT};
                color: {c.TEXT};
                border: 1px solid {c.BORDER_SUBTLE};
                border-radius: 6px;
                gridline-color: {c.TABLE_GRID};
                outline: none;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {c.TABLE_HEADER_BG};
                color: {c.PRIMARY_DIM};
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid {c.PRIMARY_DIM};
                font-weight: 600;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                font-size: 12px;
                outline: none;
            }}
        """

    # ─── Panels ───────────────────────────────────────────────────────

    @classmethod
    def details_panel_style(cls):
        c = cls.COLORS
        return f"""
            QFrame {{
                background-color: {c.CARD};
                border: 1px solid {c.BORDER};
                border-radius: 10px;
            }}
        """

    @classmethod
    def section_frame_style(cls):
        """For section containers like Known Devices, Stored Services."""
        c = cls.COLORS
        return f"background-color: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 10px; padding: 16px;"

    # ─── Labels ───────────────────────────────────────────────────────

    @classmethod
    def section_title_style(cls):
        c = cls.COLORS
        return f"color: {c.PRIMARY_DIM}; font-size: 15px; font-weight: 600; letter-spacing: 1.5px; border: none;"

    @classmethod
    def field_label_style(cls):
        c = cls.COLORS
        return f"color: {c.TEXT}; font-weight: 600; border: none; font-size: 13px;"

    @classmethod
    def detail_label_style(cls):
        c = cls.COLORS
        return f"color: {c.MUTED}; font-size: 13px; border: none; padding: 3px 0;"

    @classmethod
    def status_label_style(cls):
        c = cls.COLORS
        return f"color: {c.MUTED}; font-size: 13px;"

    @classmethod
    def panel_title_style(cls):
        c = cls.COLORS
        return f"color: {c.TEXT_BRIGHT}; font-size: 16px; font-weight: 600; border: none; padding-bottom: 10px;"

    @classmethod
    def empty_state_style(cls):
        c = cls.COLORS
        return f"color: {c.MUTED}; font-size: 15px; font-style: italic; background-color: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 8px; padding: 40px;"

    @classmethod
    def muted_label_style(cls):
        c = cls.COLORS
        return f"color: {c.MUTED}; font-size: 13px; border: none;"

    @classmethod
    def no_data_label_style(cls):
        c = cls.COLORS
        return f"color: {c.MUTED}; font-style: italic; border: none; font-size: 12px;"

    # ─── Hygiene Badges ───────────────────────────────────────────────

    @classmethod
    def hygiene_badge_style(cls):
        c = cls.COLORS
        return f"color: {c.TEXT}; font-size: 12px; padding: 4px 10px; background-color: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 6px;"

    @classmethod
    def hygiene_btn_style(cls):
        c = cls.COLORS
        return f"background-color: transparent; color: {c.PRIMARY_DIM}; font-size: 11px; padding: 3px 10px; border-radius: 4px; border: 1px solid {c.BORDER};"

    # ─── Inline Edit Fields (Details Panel) ───────────────────────────

    @classmethod
    def inline_edit_style(cls):
        c = cls.COLORS
        return f"background-color: {c.SURFACE}; color: {c.TEXT}; border: 1px solid {c.BORDER}; padding: 6px; border-radius: 6px; font-size: 13px;"

    # ─── Apply Theme ──────────────────────────────────────────────────

    @classmethod
    def apply_theme(cls, widget):
        widget.setStyleSheet(cls.get_global_stylesheet())


# Backward compatibility aliases for older dashboard code
Colors.TEXT_MUTED = Colors.MUTED
Colors.TEXT_PRIMARY = Colors.TEXT
