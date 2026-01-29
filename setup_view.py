import cv2
import time
import sys

# === 設定エリア ===
PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
WINDOW_NAME = "Camera Position Check"

# 描画色 (B, G, R)
COLOR_CROSSHAIR = (0, 255, 255)  # 黄色
COLOR_TEXT = (0, 255, 0)         # 緑色
COLOR_SUBTEXT = (200, 200, 200)  # グレー

# === ★ここにタイムラプスプログラムと同じ設定をコピーしてください ===
CAMERAS = {
    # --- 1台目のカメラ ---
    "cam1": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.1:1.0-video-index0",
    },
    # --- 2台目のカメラ ---
    "cam2": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.2:1.0-video-index0",
    },
    # --- 3台目のカメラ ---
    "cam3": {
        "device_path": "/dev/v4l/by-path/platform-xhci-hcd.1-usb-0:1.3:1.0-video-index0",
    }
}


def open_camera(device_path):
    """指定されたデバイスパスでカメラを開く（失敗時はインデックスで再試行）"""
    print(f"デバイスを開いています: {device_path}")
    cap = cv2.VideoCapture(device_path)
    
    if not cap.isOpened():
        print("⚠️ パスでの接続に失敗しました。インデックス番号での接続を試みます...")
        try:
            # "/dev/video2" -> 2 のように数字を抽出
            import re
            match = re.search(r'video(\d+)', device_path)
            if match:
                dev_idx = int(match.group(1))
            else:
                # パスに数字が含まれない場合は推測が難しいため0などを試す手もあるが、ここでは単純化
                dev_idx = -1 
            
            if dev_idx >= 0:
                print(f"🔄 インデックス {dev_idx} で再試行中...")
                cap = cv2.VideoCapture(dev_idx)
        except Exception as e:
            print(f"❌ 再試行エラー: {e}")

    return cap


def draw_overlay(frame, camera_name, camera_idx, total_cameras, device_path):
    """プレビュー画面にガイド線と情報を描画する"""
    # リサイズ
    display_frame = cv2.resize(frame, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
    
    # 中心座標
    cx = PREVIEW_WIDTH // 2
    cy = PREVIEW_HEIGHT // 2
    
    # 十字ガイド線 (センター合わせ用)
    cv2.line(display_frame, (cx, 0), (cx, PREVIEW_HEIGHT), COLOR_CROSSHAIR, 1)
    cv2.line(display_frame, (0, cy), (PREVIEW_WIDTH, cy), COLOR_CROSSHAIR, 1)

    # 情報テキスト表示
    info_text = f"[{camera_name}] {camera_idx + 1}/{total_cameras}"
    cv2.putText(display_frame, info_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_TEXT, 2, cv2.LINE_AA)
    
    # デバイスパス表示（小さく）
    cv2.putText(display_frame, device_path, (10, PREVIEW_HEIGHT - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_SUBTEXT, 1, cv2.LINE_AA)
    
    return display_frame


def main():
    camera_keys = list(CAMERAS.keys())
    if not camera_keys:
        print("❌ 設定されたカメラがありません。CAMERASを確認してください。")
        return

    current_idx = 0
    cap = None
    
    # 初期カメラを開く
    current_key = camera_keys[current_idx]
    current_path = CAMERAS[current_key]["device_path"]
    cap = open_camera(current_path)

    cv2.namedWindow(WINDOW_NAME)
    
    print("\n=== 操作方法 ===")
    print(" [←] または [b] : 前のカメラへ")
    print(" [→] または [n] : 次のカメラへ")
    print(" [q] : 終了")
    print("================")

    try:
        while True:
            # フレーム読み込み
            ret = False
            if cap and cap.isOpened():
                ret, frame = cap.read()
            
            if ret:
                # 描画処理
                preview_img = draw_overlay(
                    frame, 
                    camera_keys[current_idx], 
                    current_idx, 
                    len(camera_keys), 
                    CAMERAS[camera_keys[current_idx]]["device_path"]
                )
                cv2.imshow(WINDOW_NAME, preview_img)
            else:
                # 映像が取れない場合の待機画面（黒画面など）を出しても良いが、ここでは少し待つ
                time.sleep(0.1)

            # キー入力待機
            key = cv2.waitKey(10) & 0xFF

            if key == ord('q'):
                break
            
            # カメラ切り替え判定
            new_idx = current_idx
            if key == 81 or key == ord('b'):  # 左矢印 or b
                new_idx = (current_idx - 1) % len(camera_keys)
            elif key == 83 or key == ord('n'):  # 右矢印 or n
                new_idx = (current_idx + 1) % len(camera_keys)
            
            # インデックスが変わったら切り替え処理
            if new_idx != current_idx:
                print(f"\n🔄 カメラ切り替え: {camera_keys[new_idx]}")
                
                # 前のカメラを閉じる
                if cap:
                    cap.release()
                time.sleep(0.5) # エラー防止のウェイト
                
                # 新しいカメラを開く
                current_idx = new_idx
                current_key = camera_keys[current_idx]
                current_path = CAMERAS[current_key]["device_path"]
                cap = open_camera(current_path)

    except KeyboardInterrupt:
        print("\n🛑 強制終了")
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        print("✅ 終了しました")

if __name__ == "__main__":
    main()