from .models import Footer, TherapyMethod, CustomCode

def footer_context(request):
    return {
        'footer': Footer.objects.last(),
        'therapy_methods': TherapyMethod.objects.order_by('order')
    }

def custom_code_context(request):
    try:
        custom_code = CustomCode.objects.last()
    except CustomCode.DoesNotExist:
        custom_code = None
    return {
        'custom_css': custom_code.css_code if custom_code else '',
        'custom_js': custom_code.js_code if custom_code else ''
    }