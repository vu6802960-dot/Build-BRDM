import csv
import io
from datetime import datetime
from kivy.utils import platform

def export_to_csv(data):
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
        # utf-8-sig giúp Excel hiển thị đúng các ký tự
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in data:
                writer.writerow([r['datetime'], r['model'], r['imei'], r['smsn'], r['status'], r['person']])
        return True
    except Exception as e:
        print(f"Desktop Export Error: {e}")
        return False

def export_android_csv(data, filename, headers):
    try:
        from jnius import autoclass
        from android import activity
        
        # Sử dụng Intent để người dùng chọn vị trí lưu file
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType('text/csv')
        intent.putExtra(Intent.EXTRA_TITLE, filename)
        
        def on_activity_result(request_code, result_code, intent_data):
            if result_code == -1 and intent_data: # -1 là RESULT_OK
                uri = intent_data.getData()
                write_to_uri(uri, data, headers)
        
        activity.bind(on_activity_result=on_activity_result)
        current_activity = autoclass('org.kivy.android.PythonActivity').mActivity
        current_activity.startActivityForResult(intent, 1001)
        return True
    except Exception as e:
        print(f"Android Export Error: {e}")
        return False

def write_to_uri(uri, data, headers):
    from jnius import autoclass
    context = autoclass('org.kivy.android.PythonActivity').mActivity
    out_stream = context.getContentResolver().openOutputStream(uri)
    
    output = io.StringIO()
    # Ghi BOM cho Excel
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in data:
        writer.writerow([r['datetime'], r['model'], r['imei'], r['smsn'], r['status'], r['person']])
    
    out_stream.write(output.getvalue().encode('utf-8'))
    out_stream.close()