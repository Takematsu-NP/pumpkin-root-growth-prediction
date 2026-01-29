import os
import time
import datetime
import smtplib
import ssl
import subprocess
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, List, Optional

import cv2
from dotenv import load_dotenv

# 環境変数を読み込む (.envファイル)
load_dotenv()

# === 設定エリア ===
CAPTURE_INTERVAL_SECONDS = 3600  # 1時間ごとに撮影

# Gmail設定 (環境変数から取得)
GMAIL_ACCOUNT = os.getenv("GMAIL_ACCOUNT")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO", GMAIL_ACCOUNT)  # 指定がなければ自分宛て

# USB Hub設定 (uhubctlで使用するポート)
USB_HUBS = ["1", "2", "3", "4"]

# カメラ設定
CAMERAS = {
    "cam1": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.1:1.0-video-index0",
        "save_dir": os.path.expanduser("~/Pictures/plant10"),
        "settings": {
            "exposure_time_absolute": 140,
            "gain": 0,
            "white_balance_temperature": 6500,
            "hue": 2,
            "brightness": -19,
            "contrast": 32
        }
    },
    "cam2": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.2:1.0-video-index0",
        "save_dir": os.path.expanduser("~/Pictures/plant11"),
        "settings": {
            "exposure_time_absolute": 140,
            "gain": 0,
            "white_balance_temperature": 6500,
            "hue": 2,
            "brightness": -19,
            "contrast": 32
        }
    },
    "cam3": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
        "save_dir": os.path.expanduser("~/Pictures/plant12"),
        "settings": {
            "exposure_time_absolute": 140,
            "gain": 0,
            "white_balance_temperature": 6500,
            "hue": 2,
            "brightness": -19,
            "contrast": 32
        }
    }
}


def send_mail_with_image(subject: str, body: str, image_paths: List[str]):
    """Gmailで画像を添付してメール送信"""
    if not GMAIL_ACCOUNT or not GMAIL_PASSWORD:
        print("⚠️ Gmailの環境変数が設定されていません。メール送信をスキップします。")
        return

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = GMAIL_ACCOUNT
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(body, "plain"))

    attached_count = 0
    try:
        for img_path in image_paths:
            if img_path and os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=os.path.basename(img_path)
                    )
                    msg.attach(img)
                attached_count += 1

        if attached_count > 0:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
                server.send_message(msg)
            print(f"📧 メール送信成功: {subject}")
        else:
            print("⚠️ 送信する画像がありませんでした")

    except Exception as e:
        print(f"⚠️ メール送信失敗: {e}")


def apply_camera_settings(device_path: str, settings: Dict):
    """v4l2-ctlを使用してカメラの設定を適用"""
    cmd_base = ["v4l2-ctl", "-d", device_path]
    try:
        # 基本設定
        subprocess.run(cmd_base + ["--set-ctrl=auto_exposure=1"], check=True)
        subprocess.run(cmd_base + ["--set-ctrl=white_balance_automatic=0"], check=True)

        # 個別パラメータ設定
        for key, val in settings.items():
            subprocess.run(cmd_base + [f"--set-ctrl={key}={val}"], check=True)

        time.sleep(0.5)  # 反映待ち
    except subprocess.CalledProcessError as e:
        print(f"⚠️ 設定コマンドエラー ({device_path}): {e}")
    except Exception as e:
        print(f"⚠️ 設定予期せぬエラー ({device_path}): {e}")


def take_photo(key: str, config: Dict) -> Optional[str]:
    """写真を撮影して保存する"""
    device_path = config["device_path"]
    save_dir = config["save_dir"]
    
    # 保存ディレクトリ作成
    os.makedirs(save_dir, exist_ok=True)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{now}.jpg"
    full_path = os.path.join(save_dir, filename)

    print(f"💡 [{key}] カメラ設定適用中... ({device_path})")
    apply_camera_settings(device_path, config["settings"])

    # 撮影 (最大解像度設定)
    cap = cv2.VideoCapture(device_path)
    if not cap.isOpened():
        print(f"⚠️ [{key}] カメラを開けませんでした。パスを確認してください。")
        return None

    # 高解像度 (2592 x 1944) 設定
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)

    time.sleep(2)  # カメラ安定待ち
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(full_path, frame)
        print(f"✅ [{key}] 撮影成功: {filename}")
        return full_path
    else:
        print(f"⚠️ [{key}] 画像取得失敗")
        return None


def control_usb_ports(state: int):
    """USBポートの電源制御 (uhubctl) state: 1(ON) or 0(OFF)"""
    action = "ON" if state else "OFF"
    print(f"⚡ USBポートを {action} にします...")
    
    for hub in USB_HUBS:
        try:
            subprocess.run(
                ["sudo", "uhubctl", "-l", hub, "-a", str(state)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
        except Exception:
            pass
    
    time.sleep(1)
    if state:
        print("...カメラ認識待ち 15秒...")
        time.sleep(15)
    else:
        print("⚙️ USB OFF 完了")


def main():
    print("📸 3台体制タイムラプスシステム起動")
    
    # 初期化：一旦OFFにする
    control_usb_ports(0)
    time.sleep(2)

    try:
        while True:
            # 1. USB電源ON
            control_usb_ports(1)
            
            now_str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
            print(f"\n📸 撮影シーケンス開始 {now_str}")
            
            captured_images = []

            # 2. カメラリストを順番に処理
            for cam_key, cam_config in CAMERAS.items():
                path = take_photo(cam_key, cam_config)
                if path:
                    captured_images.append(path)
            
            # 3. まとめてメール送信
            if captured_images:
                send_mail_with_image(
                    f"📸 定期撮影完了 ({now_str})", 
                    f"{len(captured_images)}台のカメラで撮影しました。", 
                    captured_images
                )
            else:
                print("⚠️ 写真が1枚も撮れませんでした。")

            # 4. USB電源OFF
            print("🔌 待機のためUSBポートをOFFにします。")
            control_usb_ports(0)

            print(f"⏳ 次の撮影まで {CAPTURE_INTERVAL_SECONDS} 秒待機...\n")
            time.sleep(CAPTURE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n🛑 手動停止されました")
    finally:
        print("✅ 終了処理: USBポートをOFFにします")
        control_usb_ports(0)


if __name__ == "__main__":
    main()