#channel bots @ih_py Telegram ®
import telebot
import subprocess
import os
import sys
import time
import threading
import logging
import platform
import json
import hashlib
import secrets
from datetime import datetime
from telebot import types

#متغيرات

bot_token = "8984632154:AAHANBKCgoveFQ2MMchhl4vsXc-71GJOBMg" #توكنك
ADMIN_IDS = [8823091956]  #ايديك
ALLOWED_USERS = []  #لاتضف هنا أي شي

#فقط

bot = telebot.TeleBot(bot_token)


uploaded_files_count = 0
current_file_name = "moon.py"
running_process = None
active_sessions = {}
user_files = {}  
bot_start_time = time.time()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_logs.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_system_info():
    """الحصول على معلومات النظام"""
    info = {}
    
    try:
        
        info['system'] = platform.system()
        info['node'] = platform.node()
        info['release'] = platform.release()
        info['version'] = platform.version()
        info['machine'] = platform.machine()
        info['processor'] = platform.processor()
        
        
        info['python_version'] = platform.python_version()
        
       
        if hasattr(os, 'cpu_count'):
            info['cpu_count'] = os.cpu_count()
        else:
            info['cpu_count'] = "غير معروف"
            
        return info
    except Exception as e:
        logger.error(f"خطأ في الحصول على معلومات النظام: {e}")
        return {"error": str(e)}

def get_server_stats():
    
    try:
        stats_text = ""
        
        
        sys_info = get_system_info()
        
        stats_text += f"معلومات الخادم:\n\n"
        stats_text += f"النظام: {sys_info.get('system', 'غير معروف')}\n"
        stats_text += f"الإصدار: {sys_info.get('release', 'غير معروف')}\n"
        stats_text += f"بايثون: {sys_info.get('python_version', 'غير معروف')}\n"
        
        
        if platform.system() in ['Linux', 'Darwin']:
            try:
                if platform.system() == 'Linux':
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = {}
                        for line in f:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                meminfo[key.strip()] = value.strip()
                        
                        total_mem = int(meminfo.get('MemTotal', '0 kB').split()[0]) / 1024
                        free_mem = int(meminfo.get('MemFree', '0 kB').split()[0]) / 1024
                        used_mem = total_mem - free_mem
                        mem_percent = (used_mem / total_mem) * 100 if total_mem > 0 else 0
                        
                        stats_text += f"الذاكرة: {mem_percent:.1f}% ({used_mem:.1f}MB / {total_mem:.1f}MB)\n"
                else:
                    
                    proc = subprocess.Popen(['sysctl', '-n', 'hw.memsize'], stdout=subprocess.PIPE, text=True)
                    mem_size = int(proc.communicate()[0].strip()) / (1024**3)
                    stats_text += f"الذاكرة: {mem_size:.1f} جيجابايت\n"
                        
            except:
                stats_text += "الذاكرة: غير متاح\n"
        else:
           
            try:
                import ctypes
                
                
                kernel32 = ctypes.windll.kernel32
                ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory.restype = ctypes.c_ulonglong
                
                total_mem = kernel32.GetPhysicallyInstalledSystemMemory() / 1024
                total_mem_mb = total_mem / 1024
                
                stats_text += f"الذاكرة: {total_mem_mb:.1f} ميجابايت\n"
            except:
                stats_text += "الذاكرة: غير متاح\n"
        
        
        try:
            if platform.system() == 'Windows':
                import ctypes
                
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p('/'), 
                    None, 
                    ctypes.pointer(total_bytes), 
                    ctypes.pointer(free_bytes)
                )
                
                total_gb = total_bytes.value / (1024**3)
                free_gb = free_bytes.value / (1024**3)
                used_gb = total_gb - free_gb
                used_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0
                
                stats_text += f"التخزين: {used_percent:.1f}% ({used_gb:.1f}جيجابايت / {total_gb:.1f}جيجابايت)\n"
            else:
                
                statvfs = os.statvfs('/')
                
                total_bytes = statvfs.f_frsize * statvfs.f_blocks
                free_bytes = statvfs.f_frsize * statvfs.f_bfree
                used_bytes = total_bytes - free_bytes
                
                total_gb = total_bytes / (1024**3)
                used_gb = used_bytes / (1024**3)
                used_percent = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                
                stats_text += f"التخزين: {used_percent:.1f}% ({used_gb:.1f}جيجابايت / {total_gb:.1f}جيجابايت)\n"
        except:
            stats_text += "التخزين: غير متاح\n"
        
        
        uptime_seconds = time.time() - bot_start_time
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
        
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        stats_text += f"مدة التشغيل: {uptime_str}\n"
        stats_text += f"الوقت الحالي: {current_time}\n"
        
        
        try:
            files = [f for f in os.listdir('.') if f.endswith('.py')]
            stats_text += f"الملفات النشطة: {len(files)}\n"
        except:
            stats_text += f"الملفات النشطة: غير متاح\n"
        
        return stats_text
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة الخادم: {e}")
        return f"خطأ في جلب معلومات الخادم: {e}"

def get_cpu_usage():
    
    try:
        if platform.system() == 'Linux':
            
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read().strip().split()
                return f"تحميل النظام: {loadavg[0]} (1 دقيقة)"
        elif platform.system() == 'Darwin':
            
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            return f"المعالج: {result.stdout.strip()}"
        else:
            
            return "المعالج: غير متاح"
    except:
        return "المعالج: غير متاح"

def get_process_count():
    
    try:
        if platform.system() == 'Windows':
            
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            
            class PERFORMANCE_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.c_ulong),
                    ("CommitTotal", ctypes.c_size_t),
                    ("CommitLimit", ctypes.c_size_t),
                    ("CommitPeak", ctypes.c_size_t),
                    ("PhysicalTotal", ctypes.c_size_t),
                    ("PhysicalAvailable", ctypes.c_size_t),
                    ("SystemCache", ctypes.c_size_t),
                    ("KernelTotal", ctypes.c_size_t),
                    ("KernelPaged", ctypes.c_size_t),
                    ("KernelNonpaged", ctypes.c_size_t),
                    ("PageSize", ctypes.c_size_t),
                    ("HandleCount", ctypes.c_ulong),
                    ("ProcessCount", ctypes.c_ulong),
                    ("ThreadCount", ctypes.c_ulong),
                ]
            
            perf_info = PERFORMANCE_INFORMATION()
            perf_info.cb = ctypes.sizeof(PERFORMANCE_INFORMATION)
            
            if kernel32.GetPerformanceInfo(ctypes.byref(perf_info), perf_info.cb):
                return perf_info.ProcessCount
        else:
            
            try:
                # استخدام أمر ps
                result = subprocess.run(['ps', '-e', '--no-headers'], 
                                      capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                return len([line for line in lines if line.strip()])
            except:
                
                try:
                    result = subprocess.run(['ps', 'aux'], 
                                          capture_output=True, text=True)
                    lines = result.stdout.strip().split('\n')
                    return max(0, len(lines) - 1)
                except:
                    pass
    except Exception as e:
        logger.error(f"خطأ في الحصول على عدد العمليات: {e}")
    
    return "غير متاح"


def is_admin(user_id):
    
    return user_id in ADMIN_IDS

def is_allowed(user_id):
    
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS or user_id in ADMIN_IDS

def generate_session_id():
    
    return secrets.token_hex(16)

def log_activity(user_id, action, details=""):
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] المستخدم {user_id} - {action} {details}"
    logger.info(log_msg)
    
    
    with open("activity_log.txt", "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def get_file_info(file_path):
    
    try:
        size = os.path.getsize(file_path)
        modified = time.ctime(os.path.getmtime(file_path))
        created = time.ctime(os.path.getctime(file_path))
        
        
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        
        return {
            'size': size,
            'size_mb': size / (1024*1024),
            'modified': modified,
            'created': created,
            'hash': file_hash
        }
    except:
        return None


def create_main_menu():
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    
    upload_btn = types.InlineKeyboardButton("رفع ملف", callback_data="upload")
    files_btn = types.InlineKeyboardButton("قائمة الملفات", callback_data="list_files")
    delete_all_btn = types.InlineKeyboardButton("حذف الكل", callback_data="delete_all")
    
    
    run_btn = types.InlineKeyboardButton("تشغيل", callback_data="run_file")
    stop_btn = types.InlineKeyboardButton("إيقاف", callback_data="stop_process")
    processes_btn = types.InlineKeyboardButton("العمليات", callback_data="show_processes")
    
    
    stats_btn = types.InlineKeyboardButton("حالة الخادم", callback_data="server_stats")
    restart_btn = types.InlineKeyboardButton("إعادة تشغيل", callback_data="restart_bot")
    sysinfo_btn = types.InlineKeyboardButton("معلومات النظام", callback_data="system_info")
    
    
    logs_btn = types.InlineKeyboardButton("السجلات", callback_data="show_logs")
    clear_logs_btn = types.InlineKeyboardButton("تنظيف السجلات", callback_data="clear_logs")
    
   
    keyboard.row(upload_btn, files_btn)
    keyboard.row(run_btn, stop_btn, processes_btn)
    keyboard.row(stats_btn, sysinfo_btn, restart_btn)
    keyboard.row(logs_btn, clear_logs_btn)
    keyboard.row(delete_all_btn)
    
    return keyboard

def create_file_menu(file_name):
    
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    
    run_btn = types.InlineKeyboardButton("تشغيل", callback_data=f"run_{file_name}")
    delete_btn = types.InlineKeyboardButton("حذف", callback_data=f"delete_{file_name}")
    info_btn = types.InlineKeyboardButton("معلومات", callback_data=f"info_{file_name}")
    back_btn = types.InlineKeyboardButton("رجوع", callback_data="back_to_main")
    
    keyboard.row(run_btn, delete_btn, info_btn)
    keyboard.row(back_btn)
    
    return keyboard


@bot.message_handler(commands=["start"])
def start_message(message):
    """معالجة أمر /start"""
    user_id = message.from_user.id
    
    if not is_allowed(user_id):
        bot.reply_to(message, "غير مصرح لك باستخدام هذا البوت.")
        log_activity(user_id, "محاولة دخول غير مصرح")
        return
    
    
    session_id = generate_session_id()
    active_sessions[user_id] = {
        'session_id': session_id,
        'last_active': time.time(),
        'username': message.from_user.username or message.from_user.first_name
    }
    
    log_activity(user_id, "بدأ المحادثة", f"المعرف: {session_id}")
    
    welcome_msg = f"""
مرحباً بك في بوت استضافة ملفات المتقدم!

مميزات البوت:
رفع وتشغيل ملفات بايثون
مراقبة حالة الخادم
نظام أمان متقدم
سجلات تفصيلية
إدارة العمليات

الإعدادات:
المستخدم: {message.from_user.first_name}
المعرف: {user_id}
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
النظام: {platform.system()}

استخدم الأزرار للتحكم في البوت
"""
    
    bot.reply_to(message, welcome_msg, reply_markup=create_main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=["stats"])
def stats_command(message):
   
    if not is_allowed(message.from_user.id):
        return
    
    stats = get_server_stats()
    bot.reply_to(message, stats, parse_mode="Markdown")
    log_activity(message.from_user.id, "طلب حالة الخادم")

@bot.message_handler(commands=["sysinfo"])
def sysinfo_command(message):
    
    if not is_allowed(message.from_user.id):
        return
    
    sys_info = get_system_info()
    
    info_msg = "معلومات النظام:\n\n"
    for key, value in sys_info.items():
        info_msg += f"{key}: {value}\n"
    
    bot.reply_to(message, info_msg, parse_mode="Markdown")

@bot.message_handler(commands=["admin"])
def admin_command(message):
    """أوامر المشرف"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "هذا الأمر للمشرفين فقط.")
        return
    
    admin_msg = """
قائمة أوامر المشرف:

إدارة الملفات:
/delete_all - حذف جميع الملفات
/clean_temp - تنظيف الملفات المؤقتة

المعلومات:
/stats - حالة الخادم
/sysinfo - معلومات النظام
/users - المستخدمين النشطين
/logs - عرض السجلات

الإعدادات:
/broadcast - إرسال رسالة للجميع
/restart - إعادة تشغيل البوت
"""
    
    bot.reply_to(message, admin_msg)

@bot.message_handler(commands=["clean_temp"])
def clean_temp(message):
    
    if not is_admin(message.from_user.id):
        return
    
    try:
        temp_files = [f for f in os.listdir('.') 
                     if f.endswith('.tmp') or f.endswith('.log') or f.endswith('.txt')]
        count = 0
        
        for file in temp_files:
            if file not in ['bot_logs.txt', 'activity_log.txt']:
                os.remove(file)
                count += 1
        
        bot.reply_to(message, f"تم تنظيف {count} ملف مؤقت.")
        log_activity(message.from_user.id, "تنظيف الملفات المؤقتة")
    except Exception as e:
        bot.reply_to(message, f"خطأ في التنظيف: {e}")

@bot.message_handler(commands=["users"])
def show_users(message):
   
    if not is_admin(message.from_user.id):
        return
    
    if not active_sessions:
        bot.reply_to(message, "لا يوجد مستخدمين نشطين.")
        return
    
    users_msg = "المستخدمين النشطين:\n\n"
    
    current_time = time.time()
    for user_id, session in active_sessions.items():
        last_active_min = (current_time - session['last_active']) / 60
        username = session.get('username', 'غير معروف')
        
        users_msg += f"{username} (المعرف: {user_id})\n"
        users_msg += f"   النشاط الأخير: منذ {last_active_min:.1f} دقيقة\n"
        users_msg += f"   رقم الجلسة: {session['session_id'][:8]}...\n\n"
    
    bot.reply_to(message, users_msg, parse_mode="Markdown")


@bot.message_handler(content_types=["document"])
def handle_file(message):
    
    user_id = message.from_user.id
    
    if not is_allowed(user_id):
        bot.reply_to(message, "غير مصرح لك برفع الملفات.")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = message.document.file_name
        
        
        if not file_name.endswith('.py'):
            bot.reply_to(message, "يرجى رفع ملفات بايثون فقط (.py)")
            return
        
        
        if len(downloaded_file) > 10 * 1024 * 1024:
            bot.reply_to(message, "حجم الملف كبير جداً! الحد الأقصى 10 ميجابايت")
            return
        
        
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        global uploaded_files_count
        uploaded_files_count += 1
        
        
        if user_id not in user_files:
            user_files[user_id] = []
        user_files[user_id].append(file_name)
        
        
        file_info_data = get_file_info(file_name)
        
        success_msg = f"""
تم رفع الملف بنجاح!

اسم الملف: {file_name}
الحجم: {file_info_data['size_mb']:.2f} ميجابايت
الرقم التعريفي: {file_info_data['hash']}
تاريخ الرفع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

يمكنك الآن التحكم في الملف عبر الأزرار 
"""
        
        bot.reply_to(message, success_msg, 
                    reply_markup=create_file_menu(file_name),
                    parse_mode="Markdown")
        
        log_activity(user_id, "رفع ملف", f"اسم الملف: {file_name}")
        
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء رفع الملف: {e}")
        logger.error(f"خطأ في رفع الملف: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
   
    user_id = call.from_user.id
    
    if not is_allowed(user_id):
        bot.answer_callback_query(call.id, "غير مصرح لك باستخدام هذا البوت.")
        return
    
    try:
        
        if user_id in active_sessions:
            active_sessions[user_id]['last_active'] = time.time()
        
        
        if call.data == 'upload':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "أرسل ملف بايثون لرفعه على الخادم...")
        
        
        elif call.data == 'list_files':
            files = [f for f in os.listdir('.') if f.endswith('.py')]
            
            if not files:
                bot.edit_message_text("لا توجد ملفات مرفوعة بعد.",
                                    call.message.chat.id,
                                    call.message.message_id)
                return
            
            files_list = "الملفات المرفوعة:\n\n"
            for i, file in enumerate(files, 1):
                size = os.path.getsize(file) / 1024
                files_list += f"{i}. {file} ({size:.1f} كيلوبايت)\n"
            
            files_list += "\nاختر ملفاً من القائمة للتحكم به"
            
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            
            for file in files:
                btn = types.InlineKeyboardButton(f"{file[:15]}", callback_data=f"select_{file}")
                buttons.append(btn)
            
            
            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    keyboard.row(buttons[i], buttons[i+1])
                else:
                    keyboard.row(buttons[i])
            
            back_btn = types.InlineKeyboardButton("رجوع", callback_data="back_to_main")
            keyboard.row(back_btn)
            
            bot.edit_message_text(files_list,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=keyboard,
                                parse_mode="Markdown")
        
        
        elif call.data.startswith('select_'):
            file_name = call.data.replace('select_', '')
            
            file_info = get_file_info(file_name)
            if file_info:
                file_msg = f"""
معلومات الملف:

الاسم: {file_name}
الحجم: {file_info['size_mb']:.2f} ميجابايت
التعديل الأخير: {file_info['modified']}
الرقم التعريفي: {file_info['hash']}

اختر الإجراء المناسب:
"""
                bot.edit_message_text(file_msg,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=create_file_menu(file_name),
                                    parse_mode="Markdown")
        
        
        elif call.data == 'delete_all':
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "هذا الأمر للمشرفين فقط.")
                return
            
            
            keyboard = types.InlineKeyboardMarkup()
            confirm_btn = types.InlineKeyboardButton("تأكيد الحذف", callback_data="confirm_delete_all")
            cancel_btn = types.InlineKeyboardButton("إلغاء", callback_data="back_to_main")
            keyboard.row(confirm_btn, cancel_btn)
            
            bot.edit_message_text("هل أنت متأكد من حذف جميع الملفات؟\n\nهذا الإجراء لا يمكن التراجع عنه!",
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=keyboard,
                                parse_mode="Markdown")
        
       
        elif call.data == 'confirm_delete_all':
            files = [f for f in os.listdir('.') if f.endswith('.py')]
            deleted_count = 0
            
            for file in files:
                try:
                    os.remove(file)
                    deleted_count += 1
                except:
                    pass
            
            bot.edit_message_text(f"تم حذف {deleted_count} ملف بنجاح.",
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=create_main_menu())
            
            log_activity(user_id, "حذف جميع الملفات", f"عدد: {deleted_count}")
        
        
        elif call.data == 'run_file':
            if not current_file_name:
                bot.answer_callback_query(call.id, "لا يوجد ملف محدد للتشغيل.")
                return
            
            run_selected_file(call, current_file_name)
        
        elif call.data.startswith('run_'):
            file_name = call.data.replace('run_', '')
            run_selected_file(call, file_name)
        
        
        elif call.data == 'stop_process':
            global running_process
            if running_process and running_process.poll() is None:
                running_process.terminate()
                running_process = None
                bot.answer_callback_query(call.id, "تم إيقاف تشغيل الملف.")
                log_activity(user_id, "إيقاف تشغيل الملف")
            else:
                bot.answer_callback_query(call.id, "لا يوجد ملف قيد التشغيل.")
        
       
        elif call.data == 'show_processes':
            processes_msg = "العمليات النشطة:\n\n"
            
            if running_process and running_process.poll() is None:
                processes_msg += f"{current_file_name} - قيد التشغيل\n"
            else:
                processes_msg += "لا توجد عمليات نشطة\n"
            
            
            process_count = get_process_count()
            processes_msg += f"\nعمليات النظام: {process_count}"
            
            bot.edit_message_text(processes_msg,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=create_main_menu(),
                                parse_mode="Markdown")
        
        
        elif call.data == 'server_stats':
            stats = get_server_stats()
            bot.edit_message_text(stats,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=create_main_menu(),
                                parse_mode="Markdown")
            
            log_activity(user_id, "عرض حالة الخادم")
        
        
        elif call.data == 'system_info':
            sys_info = get_system_info()
            
            info_msg = "معلومات النظام التفصيلية:\n\n"
            for key, value in sys_info.items():
                info_msg += f"{key.replace('_', ' ').title()}: {value}\n"
            
            bot.edit_message_text(info_msg,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=create_main_menu(),
                                parse_mode="Markdown")
        
        
        elif call.data == 'restart_bot':
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "هذا الأمر للمشرفين فقط.")
                return
            
            bot.edit_message_text("جاري إعادة تشغيل البوت...",
                                call.message.chat.id,
                                call.message.message_id)
            
            log_activity(user_id, "إعادة تشغيل البوت")
            time.sleep(2)
            os.execv(sys.executable, ['python'] + sys.argv)
        
      
        elif call.data == 'show_logs':
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "هذا الأمر للمشرفين فقط.")
                return
            
            try:
                with open("activity_log.txt", "r", encoding="utf-8") as f:
                    logs = f.read()
                
                if len(logs) > 4000:
                    logs = logs[-4000:]  
                
                logs_msg = f"آخر السجلات:\n\n{logs}"
                
                bot.edit_message_text(logs_msg,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=create_main_menu(),
                                    parse_mode="Markdown")
            except FileNotFoundError:
                bot.edit_message_text("لا توجد سجلات بعد.",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=create_main_menu())
        
        
        elif call.data == 'clear_logs':
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "هذا الأمر للمشرفين فقط.")
                return
            
            try:
                open("activity_log.txt", "w").close()
                bot.answer_callback_query(call.id, "تم تنظيف السجلات.")
            except:
                bot.answer_callback_query(call.id, "خطأ في تنظيف السجلات.")
        
       
        elif call.data.startswith('delete_'):
            file_name = call.data.replace('delete_', '')
            
            try:
                os.remove(file_name)
                bot.answer_callback_query(call.id, f"تم حذف {file_name}")
                
                
                files = [f for f in os.listdir('.') if f.endswith('.py')]
                if files:
                    bot.edit_message_text(f"تم حذف الملف.\n\nالملفات المتبقية: {len(files)}",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=create_main_menu())
                else:
                    bot.edit_message_text("تم حذف الملف.\n\nلا توجد ملفات مرفوعة.",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=create_main_menu())
                
                log_activity(user_id, "حذف ملف", f"اسم الملف: {file_name}")
            except Exception as e:
                bot.answer_callback_query(call.id, f"خطأ في الحذف: {e}")
        
        
        elif call.data.startswith('info_'):
            file_name = call.data.replace('info_', '')
            file_info = get_file_info(file_name)
            
            if file_info:
                info_msg = f"""
معلومات مفصلة عن الملف:

الاسم: {file_name}
الحجم: {file_info['size']:,} بايت ({file_info['size_mb']:.2f} ميجابايت)
تاريخ الإنشاء: {file_info['created']}
آخر تعديل: {file_info['modified']}
الرقم التعريفي: {file_info['hash']}

المسار: {os.path.abspath(file_name)}
"""
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, info_msg, parse_mode="Markdown")
        
        
        elif call.data == 'back_to_main':
            files_count = len([f for f in os.listdir('.') if f.endswith('.py')])
            
            welcome_msg = f"""
لوحة التحكم الرئيسية

إحصائيات:
الملفات المرفوعة: {files_count}
المستخدمين النشطين: {len(active_sessions)}
وقت تشغيل البوت: {time.strftime('%H:%M:%S', time.gmtime(time.time() - bot_start_time))}
النظام: {platform.system()}

اختر الإجراء المطلوب من الأزرار أدناه
"""
            
            bot.edit_message_text(welcome_msg,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=create_main_menu(),
                                parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"خطأ في الرد: {e}")
        bot.answer_callback_query(call.id, f"حدث خطأ: {e}")

def run_selected_file(call, file_name):
   
    global running_process, current_file_name
    
    if running_process and running_process.poll() is None:
        bot.answer_callback_query(call.id, "يوجد ملف قيد التشغيل بالفعل.")
        return
    
    try:
        current_file_name = file_name
        
        python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
        running_process = subprocess.Popen([python_cmd, file_name],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          text=True)
        
        monitor_thread = threading.Thread(target=monitor_process, args=(call,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        bot.answer_callback_query(call.id, f"تم تشغيل {file_name}")
        log_activity(call.from_user.id, "تشغيل ملف", f"اسم الملف: {file_name}")
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"خطأ في التشغيل: {e}")

def monitor_process(call):
    
    global running_process
    
    try:
        stdout, stderr = running_process.communicate(timeout=300)  
        
        if running_process.returncode == 0:
            output = stdout[:500] if stdout else "لا يوجد إخراج"
            status_msg = f"تم إنهاء تشغيل {current_file_name} بنجاح.\n\nالإخراج:\n{output}"
        else:
            error_msg = stderr[:500] if stderr else "خطأ غير معروف"
            status_msg = f"خطأ في تشغيل {current_file_name}:\n{error_msg}"
        
        bot.send_message(call.message.chat.id, status_msg, parse_mode="Markdown")
        
    except subprocess.TimeoutExpired:
        bot.send_message(call.message.chat.id, f"ملف {current_file_name} لا يزال قيد التشغيل...")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"خطأ في مراقبة العملية: {e}")
    
    running_process = None


def cleanup_old_sessions():
    
    while True:
        time.sleep(3600)
        current_time = time.time()
        
        to_remove = []
        for user_id, session in active_sessions.items():
            if current_time - session['last_active'] > 7200:  
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del active_sessions[user_id]
            logger.info(f"تم تنظيف جلسة المستخدم: {user_id}")


cleanup_thread = threading.Thread(target=cleanup_old_sessions)
cleanup_thread.daemon = True
cleanup_thread.start()


if __name__ == "__main__":
    logger.info("بدء تشغيل بوت ويفي المتقدم...")
    logger.info(f"نظام التشغيل: {platform.system()} {platform.release()}")
    
    if ADMIN_IDS == [7004336332]:
        logger.warning("لم يتم تعيين معرفات المشرفين! يرجى تعديل ADMIN_IDS")
    
    if not os.path.exists("activity_log.txt"):
        with open("activity_log.txt", "w", encoding="utf-8") as f:
            f.write(f"سجلات بوت استضافة\n")
            f.write(f"تاريخ البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"نظام التشغيل: {platform.system()} {platform.release()}\n")
            f.write(f"بايثون: {platform.python_version()}\n\n")
    
    print("=" * 50)
    print("تم تشغيل البوت بنجاح!")
    print(f"النظام: {platform.system()} {platform.release()}")
    print(f"بايثون: {platform.python_version()}")
    print("بوابتك الذكية لإدارة الخوادم")
    print("للدعم: يوزرك")
    print("=" * 50)
    
    try:
        bot.polling(none_stop=True, interval=1, timeout=30)
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        print(f"خطأ: {e}")
        print("جاري إعادة التشغيل...")
        time.sleep(5)
        os.execv(sys.executable, ['python'] + sys.argv)