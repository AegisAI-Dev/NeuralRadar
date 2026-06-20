"""Centralized elite cyber-tech theme for NeuralRadar.
Simple attribute-based COLORS for compatibility. Premium QSS for SOC dashboard.
"""
from PySide6.QtGui import QFont


class Colors:
    """Elite palette as attributes for easy .PRIMARY access."""
    BG_MAIN = "#050A14"
    SURFACE = "#0B1020"
    PANEL = "#111827"
    CARD = "#151F32"
    BG_CARD = CARD
    CARD_HOVER = "#1B2A44"
    BORDER = "#26364F"
    PRIMARY = "#00E5FF"
    NEURAL_BLUE = "#38BDF8"
    PURPLE = "#7C3AED"
    SECONDARY = "#7C3AED"
    SUCCESS = "#22C55E"
    WARNING = "#FACC15"
    DANGER = "#EF4444"
    MUTED = "#94A3B8"
    TEXT = "#E5E7EB"


class Theme:
    """Central theme with reusable premium stylesheets."""
    COLORS = Colors()
    FONT_FAMILY = "Segoe UI, system-ui, sans-serif"
    TITLE_SIZE = "48px"
    HEADER_SIZE = "22px"
    BODY_SIZE = "13px"
    
    @classmethod
    def get_global_stylesheet(cls):
        c = cls.COLORS
        return f"""
            QMainWindow, QWidget {{ background-color: {c.BG_MAIN}; color: {c.TEXT}; font-family: {cls.FONT_FAMILY}; }}
            QFrame, QGroupBox {{ background-color: {c.PANEL}; border: 1px solid {c.BORDER}; border-radius: 10px; }}
            .EliteCard {{ background-color: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 12px; }}
            .EliteCard:hover {{ background-color: {c.CARD_HOVER}; border-color: {c.PRIMARY}; }}
            
            QLabel#Header {{ font-size: {cls.HEADER_SIZE}; font-weight: 600; color: {c.PRIMARY}; }}
            QPushButton {{ background: {c.CARD}; color: {c.TEXT}; border: 1px solid {c.BORDER}; border-radius: 6px; padding: 10px 20px; }}
            QPushButton:hover {{ border-color: {c.PRIMARY}; background: #13213F; }}
            QPushButton[primary="true"] {{ background: {c.PRIMARY}; color: #050A14; font-weight: 600; border: none; }}
            QPushButton[primary="true"]:hover {{ background: #67f0ff; }}
            QPushButton[success="true"] {{ background: {c.SUCCESS}; color: #050A14; font-weight: 600; }}
            QPushButton[danger="true"] {{ color: {c.DANGER}; border: 1px solid {c.DANGER}; background: transparent; }}
            QPushButton[danger="true"]:hover {{ background: {c.DANGER}; color: white; }}
            
            QLineEdit, QComboBox {{ background: {c.SURFACE}; border: 1px solid {c.BORDER}; border-radius: 6px; padding: 10px; color: {c.TEXT}; }}
            QLineEdit:focus, QComboBox:focus {{ border-color: {c.PRIMARY}; }}
            
            QTableWidget, QTableView {{ background: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 8px; gridline-color: #1E2A44; selection-background-color: rgba(0,229,255,0.2); }}
            QHeaderView::section {{ background: #0A1428; color: {c.PRIMARY}; padding: 12px; border-bottom: 2px solid {c.PRIMARY}; font-weight: 600; }}
            
            QLabel[status="active"], QLabel[status="online"] {{ background: rgba(34,197,94,0.15); color: {c.SUCCESS}; border: 1px solid {c.SUCCESS}; padding: 4px 14px; border-radius: 9999px; font-size: 12px; }}
            QLabel[status="coming-soon"] {{ background: rgba(148,163,184,0.15); color: {c.MUTED}; border: 1px solid {c.MUTED}; padding: 4px 14px; border-radius: 9999px; font-size: 12px; }}
            QLabel[status="warning"] {{ background: rgba(250,204,21,0.15); color: {c.WARNING}; border: 1px solid {c.WARNING}; padding: 4px 14px; border-radius: 9999px; }}
            QLabel[status="error"] {{ background: rgba(239,68,68,0.15); color: {c.DANGER}; border: 1px solid {c.DANGER}; padding: 4px 14px; border-radius: 9999px; }}
            
            .DetailsPanel {{ background: {c.CARD}; border: 1px solid {c.BORDER}; border-radius: 12px; padding: 20px; }}
            
            QScrollBar:vertical {{ background: {c.SURFACE}; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {c.PRIMARY}; border-radius: 4px; }}
        """
    
    @classmethod
    def get_card_style(cls, is_active: bool = True, active: bool | None = None) -> str:
        """Supports both is_active= and active= for full backward compatibility."""
        if active is not None:
            is_active = active
        c = cls.COLORS
        border = c.PRIMARY if is_active else c.BORDER
        bg = c.CARD if is_active else "#0F172A"
        return f"QFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 12px; }} QFrame:hover {{ border-color: {c.PRIMARY}; }}"
    
    @classmethod
    def get_sidebar_style(cls):
        c = cls.COLORS
        return f"""
            QWidget#Sidebar {{ background-color: {c.SURFACE}; border-right: 2px solid {c.BORDER}; }}
            QLabel#Logo {{ color: {c.PRIMARY}; font-size: 26px; font-weight: 700; letter-spacing: 1.5px; }}
            QLabel#Subtitle {{ color: {c.PURPLE}; font-size: 13px; font-weight: 500; }}
            QLabel#VersionBadge {{ background: rgba(124,58,237,0.15); color: {c.PURPLE}; border: 1px solid {c.PURPLE}; border-radius: 9999px; padding: 4px 14px; font-size: 11px; }}
            QPushButton#navButton {{ background: transparent; color: {c.MUTED}; text-align: left; padding: 14px 24px; border-radius: 8px; margin: 3px 8px; }}
            QPushButton#navButton:hover {{ background-color: #1A253F; color: {c.TEXT}; }}
            QPushButton#navButton:checked {{ background-color: rgba(0,229,255,0.12); color: {c.PRIMARY}; border-left: 4px solid {c.PRIMARY}; }}
            QLabel#StatusPill {{ background: rgba(0,229,255,0.08); color: {c.MUTED}; border: 1px solid rgba(0,229,255,0.3); border-radius: 9999px; padding: 8px; font-size: 10px; text-align: center; }}
        """
    
    @classmethod
    def apply_theme(cls, widget):
        widget.setStyleSheet(cls.get_global_stylesheet())

# Backward compatibility aliases for older dashboard code
Colors.TEXT_MUTED = Colors.MUTED
Colors.TEXT_PRIMARY = Colors.TEXT
