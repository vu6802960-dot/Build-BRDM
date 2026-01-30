import csv
import io
import os
from datetime import datetime
from kivy.utils import platform

def export_to_csv(data):
    """Hàm điều hướng xuất file dựa trên nền tảng"""
    if not data:
        return False
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"BRDM_Data_{timestamp}.csv"
    headers = ['DateTime', 'Model', 'IMEI', 'SMSN', 'Status', 'Person']
    
    if platform == 'android':
        return export_android_csv(data, filename, headers)
    else:
        return export_desktop_csv(data, filename, headers)

def export_desktop_csv(data, filename, headers):
    try:
        # utf-8-sig giúp Excel hiển thị đúng các ký tự đặc biệt
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in data:
                writer.writerow([r.get('datetime'), r.get('model'), r.get('imei'), r.get('smsn'), r.get('status'), r.get('person')])
        return True
    except Exception as e:
        print(f"Export Error: {e}")
        return False

def export_android_csv(data, filename, headers):
    try:
        from jnius import autoclass
        from android import activity
        
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType('text/csv')
        intent.putExtra(Intent.EXTRA_TITLE, filename)
        
        # Thiết lập callback để nhận URI sau khi người dùng chọn chỗ lưu
        def on_activity_result(request_code, result_code, intent_data):
            if result_code == -1 and intent_data:
                uri = intent_data.getData()
                # Gọi hàm ghi dữ liệu vào URI
                _write_data_to_uri(uri, data, headers)
        
        activity.bind(on_activity_result=on_activity_result)
        current_activity = autoclass('org.kivy.android.PythonActivity').mActivity
        current_activity.startActivityForResult(intent, 1001)
        return True
    except Exception as e:
        print(f"Android SAF Error: {e}")
        return False

def _write_data_to_uri(uri, data, headers):
    """Hàm nội bộ để ghi Byte vào luồng hệ thống Android"""
    from jnius import autoclass
    context = autoclass('org.kivy.android.PythonActivity').mActivity
    out_stream = context.getContentResolver().openOutputStream(uri)
    
    output = io.StringIO()
    output.write('\ufeff') # Thêm BOM cho Excel
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in data:
        writer.writerow([r.get('datetime'), r.get('model'), r.get('imei'), r.get('smsn'), r.get('status'), r.get('person')])
    
    out_stream.write(output.getvalue().encode('utf-8'))
    out_stream.close()
