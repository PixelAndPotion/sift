from fpdf import FPDF
from datetime import datetime
import pandas as pd


#  Brand colours (RGB) 
BLUE_DARK  = (0, 51, 160)     
BLUE_MID   = (0, 82, 204)
ACCENT     = (0, 163, 224)    
WHITE      = (255, 255, 255)
CHARCOAL   = (26, 26, 26)
STEEL      = (74, 85, 104)
LIGHT_GREY = (245, 247, 250)
RED        = (180, 30, 30)
ORANGE     = (200, 100, 0)
GREEN      = (0, 120, 60)


class SIFTReport(FPDF):
    """
    Custom FPDF class for SIFT branded PDF reports.
    Inherits from FPDF and adds header/footer automatically to every page.
    """

    def header(self):
        # Dark blue header bar
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 0, 210, 18, "F")

        # SIFT branding in header
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*WHITE)
        self.set_xy(8, 5)
        self.cell(80, 8, "SIFT  |  Signal Intelligence for Financial Transactions", ln=False)

        # Date in top right
        self.set_font("Helvetica", "", 9)
        self.set_xy(130, 5)
        self.cell(70, 8, datetime.now().strftime("%d %B %Y  |  %H:%M"), align="R")
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*STEEL)
        self.cell(0, 8, f"SIFT Risk Report  |  Confidential  |  Page {self.page_no()}", align="C")


def _risk_color(risk_level: str):
    """Return RGB colour tuple based on risk level string."""
    if "Critical" in risk_level:
        return RED
    elif "High" in risk_level:
        return ORANGE
    elif "Medium" in risk_level:
        return (180, 140, 0)
    else:
        return GREEN


def generate_report(df: pd.DataFrame, summary: dict) -> bytes:
    """
    Generate a full SIFT PDF risk report.

    Parameters:
        df:       The scored transaction DataFrame (output of anomaly_detector)
        summary:  The summary stats dict (output of get_summary_stats)

    Returns:
        PDF as bytes — passed directly to Streamlit's download button
    """
    pdf = SIFTReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    #  TITLE BLOCK 
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*BLUE_DARK)
    pdf.cell(0, 10, "SIFT Transaction Risk Report", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*STEEL)
    pdf.cell(0, 6, "Signal Intelligence for Financial Transactions  —  Automated Risk Assessment", ln=True)
    pdf.ln(4)

    # Thin accent line
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    #  EXECUTIVE SUMMARY CARDS 
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_letter_spacing(1)
    pdf.cell(0, 6, "EXECUTIVE SUMMARY", ln=True)
    pdf.set_letter_spacing(0)
    pdf.ln(2)

    # 3-column summary card row
    card_w = 58
    card_h = 20
    gap = 3
    cards = [
        ("Total Transactions", str(summary["total_transactions"])),
        ("Anomalies Detected", str(summary["anomalies_detected"])),
        ("Anomaly Rate", summary["anomaly_rate"]),
        ("Critical Alerts", str(summary["critical_alerts"])),
        ("High Alerts", str(summary["high_alerts"])),
        ("Flagged Value", summary["flagged_value"]),
    ]

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    for i, (label, value) in enumerate(cards):
        col = i % 3
        row = i // 3
        x = x_start + col * (card_w + gap)
        y = y_start + row * (card_h + gap)

        # Card background
        pdf.set_fill_color(*LIGHT_GREY)
        pdf.rect(x, y, card_w, card_h, "F")

        # Top accent bar
        pdf.set_fill_color(*BLUE_DARK)
        pdf.rect(x, y, card_w, 2, "F")

        # Label
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*STEEL)
        pdf.set_xy(x + 3, y + 3)
        pdf.cell(card_w - 6, 5, label.upper())

        # Value
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*BLUE_DARK)
        pdf.set_xy(x + 3, y + 9)
        pdf.cell(card_w - 6, 8, value)

    pdf.set_y(y_start + 2 * (card_h + gap) + 4)
    pdf.ln(4)

    #  FLAGGED TRANSACTIONS TABLE 
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_letter_spacing(1)
    pdf.cell(0, 6, "FLAGGED TRANSACTIONS", ln=True)
    pdf.set_letter_spacing(0)
    pdf.ln(2)

    # Table headers
    headers = ["Time", "TXN ID", "Account", "Type", "Amount (R)", "Risk"]
    col_widths = [28, 25, 22, 38, 30, 22]

    pdf.set_fill_color(*BLUE_DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 8)

    for header, width in zip(headers, col_widths):
        pdf.cell(width, 8, header, border=0, fill=True, align="C")
    pdf.ln()

    # Table rows — only flagged (anomaly) transactions
    flagged = df[df["is_anomaly"]].copy()
    flagged = flagged.sort_values("anomaly_score").head(50)  # Max 50 rows

    pdf.set_font("Helvetica", "", 7.5)
    for i, (_, row) in enumerate(flagged.iterrows()):
        # Alternate row shading
        if i % 2 == 0:
            pdf.set_fill_color(*LIGHT_GREY)
        else:
            pdf.set_fill_color(*WHITE)

        # Risk colour for last cell
        risk_col = _risk_color(row["risk_level"])

        time_str = str(row["timestamp"])[:16] if hasattr(row["timestamp"], '__str__') else str(row["timestamp"])[:16]

        pdf.set_text_color(*CHARCOAL)
        pdf.cell(col_widths[0], 7, time_str, fill=True)
        pdf.cell(col_widths[1], 7, str(row["transaction_id"]), fill=True, align="C")
        pdf.cell(col_widths[2], 7, str(row["account"]), fill=True, align="C")
        pdf.cell(col_widths[3], 7, str(row["type"]), fill=True)
        pdf.cell(col_widths[4], 7, f"{row['amount']:,.0f}", fill=True, align="R")

        # Risk cell with colour
        pdf.set_text_color(*risk_col)
        pdf.set_font("Helvetica", "B", 7.5)
        risk_clean = row["risk_level"].replace("🔴 ", "").replace("🟠 ", "").replace("🟡 ", "").replace("🟢 ", "")
        pdf.cell(col_widths[5], 7, risk_clean, fill=True, align="C")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ln()

    pdf.ln(6)

    #  FINDINGS & RECOMMENDATIONS 
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*BLUE_DARK)
    pdf.set_letter_spacing(1)
    pdf.cell(0, 6, "FINDINGS & RECOMMENDATIONS", ln=True)
    pdf.set_letter_spacing(0)
    pdf.ln(2)

    findings = [
        ("Transaction Volume Anomaly",
         f"{summary['anomaly_rate']} of transactions in this batch were flagged as anomalous. "
         f"This exceeds the 5% threshold for routine review and warrants immediate investigation."),

        ("High-Value Risk Exposure",
         f"Total flagged transaction value: {summary['flagged_value']}. "
         "Critical and High risk transactions should be escalated to the Risk Committee within 24 hours."),

        ("After-Hours Activity",
         "Several flagged transactions occurred between 02:00 and 04:00 SAST. "
         "After-hours high-value activity is a key indicator of potential unauthorised access or fraud."),

        ("Recommended Action",
         "1. Freeze accounts with 3+ Critical flags pending manual review.  "
         "2. Cross-reference flagged transactions against KYC records.  "
         "3. Escalate foreign currency Critical flags to Compliance.  "
         "4. Re-run SIFT analysis after 24 hours to monitor pattern changes."),
    ]

    for title, body in findings:
        # Finding title
        pdf.set_fill_color(*BLUE_DARK)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 6, f"  {title}", fill=True, ln=True)

        # Finding body
        pdf.set_fill_color(*LIGHT_GREY)
        pdf.set_text_color(*CHARCOAL)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.multi_cell(0, 5, f"  {body}", fill=True)
        pdf.ln(2)

    #  DISCLAIMER 
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*STEEL)
    pdf.multi_cell(0, 4,
        "DISCLAIMER: This report is generated by SIFT — an AI-powered anomaly detection system. "
        "All findings are probabilistic and should be reviewed by a qualified risk officer before action is taken. "
        "SIFT does not constitute a definitive determination of fraudulent activity.")

    return bytes(pdf.output())
