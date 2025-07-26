# create_meeting_app/bot_scripts/google_meet_bot.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

import threading, time, os, subprocess
from datetime import datetime

from create_meeting_app.models import Screenshot

def start_audio_recorder(meeting_id: int):
    """
    Launch ffmpeg recording into media/recordings/meet_<meeting_id>_<timestamp>.wav
    Returns (subprocess.Popen, wav_path)
    """
    os.makedirs("media/recordings", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_path = f"media/recordings/meet_{meeting_id}_{timestamp}.wav"

    MONITOR = "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"
    cmd = [
        "ffmpeg", "-y",
        "-f", "pulse",
        "-i", MONITOR,
        "-ac", "1",      # mono
        "-ar", "16000",  # 16 kHz
        wav_path
    ]
    return subprocess.Popen(cmd), wav_path


def join_meeting(meeting_link: str, bot_name: str, meeting):
    # 1) Chrome setup
    options = Options()
    for arg in (
        "--use-fake-ui-for-media-stream",
        "--disable-infobars",
        "--disable-popup-blocking",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--start-maximized",
        "--alsa-output-device=loopback",
    ):
        options.add_argument(arg)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 2) Navigate & join
        driver.get(meeting_link)
        wait = WebDriverWait(driver, 30)

        # Enter bot name
        name_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Your name']")
        ))
        name_field.clear()
        name_field.send_keys(bot_name)

        # Mute mic & camera
        try:
            mic_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Turn off microphone']")
            ))
            cam_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Turn off camera']")
            ))
            mic_btn.click()
            cam_btn.click()
        except:
            pass

        # Dismiss pop-ups
        for btn in driver.find_elements(By.XPATH, "//button[contains(text(), 'Dismiss')]"):
            btn.click()

        # Hit the “Join now” (or “Ask to join”) button
        try:
            join_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Join now')]")
            ))
        except:
            join_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Ask to join')]")
            ))
        driver.execute_script("arguments[0].click();", join_btn)

        # 3) Start audio recorder—**pass meeting.id** so file is named correctly
        recorder, wav_path = start_audio_recorder(meeting.id)

        # 4) Watcher thread: on-arrival + every-30s shots + end-detection
        stop_flag = threading.Event()
        os.makedirs("media/screenshots", exist_ok=True)

        def watcher():
            # On-arrival
            arrival = f"media/screenshots/{meeting.id}_joined.png"
            driver.save_screenshot(arrival)
            Screenshot.objects.create(meeting=meeting, image_path=arrival)

            # Periodic loop
            while not stop_flag.is_set():
                # Sleep in 1s steps for quick flag-checking
                for _ in range(30):
                    if stop_flag.is_set():
                        return
                    time.sleep(1)

                try:
                    # Detect meeting end
                    ended = driver.find_elements(By.XPATH,
                        "//div[contains(text(),'Call ended') "
                        "or contains(text(),'You left the call')]"
                    )
                    if ended:
                        stop_flag.set()
                        return

                    # Take next shot
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shot = f"media/screenshots/{meeting.id}_{ts}.png"
                    driver.save_screenshot(shot)
                    Screenshot.objects.create(meeting=meeting, image_path=shot)

                except WebDriverException:
                    stop_flag.set()
                    return

        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()

        # 5) Wait for meeting to end
        stop_flag.wait()

    finally:
        # 6) Cleanup
        try:    recorder.terminate()
        except: pass
        try:    driver.quit()
        except: pass


# Quick local test
if __name__ == "__main__":
    dummy = type("M", (), {"id": 0})
    join_meeting("https://meet.google.com/uou-rsvo-epg", "TestBot", dummy)
