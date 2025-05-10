import io
import barcode
import qrcode
from barcode.writer import SVGWriter
from base64 import b64encode


def generate_barcode_svg(code):
    """Generate a barcode SVG for the given code."""
    # Use QR code instead of linear barcode for square format
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    
    # Create an SVG image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to SVG-like XML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to a data URL compatible form
    encoded = b64encode(buffer.getvalue()).decode('utf-8')
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 250 250"><image href="data:image/png;base64,{encoded}" width="250" height="250"/></svg>'
    
    return svg_content


def generate_qr_code_svg(code):
    """Generate a QR code SVG for the given code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    
    # Create an SVG image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to SVG-like XML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to a data URL compatible form
    encoded = b64encode(buffer.getvalue()).decode('utf-8')
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 250 250"><image href="data:image/png;base64,{encoded}" width="250" height="250"/></svg>'
    
    return svg_content


def generate_barcode_data_uri(code):
    """Generate a data URI for a QR code image."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    
    # Create an SVG image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Encode to base64
    encoded = b64encode(buffer.getvalue()).decode('utf-8')
    
    # Return as a data URI
    return f"data:image/png;base64,{encoded}"


# Keep the original barcode function for backward compatibility
def generate_linear_barcode_svg(code):
    """Generate a linear barcode SVG for the given code."""
    # Create a barcode object (Code128 is a common format that works well for alphanumeric data)
    code128 = barcode.get_barcode_class('code128')
    
    # Create the barcode
    rv = io.BytesIO()
    code128(code, writer=SVGWriter()).write(rv)
    
    # Get the SVG content
    svg_content = rv.getvalue().decode('utf-8')
    
    return svg_content
