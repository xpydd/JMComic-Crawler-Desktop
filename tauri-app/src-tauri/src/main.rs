#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Serialize, Deserialize)]
struct DownloadResult {
    success: bool,
    message: String,
}

fn parse_download_output(output: std::process::Output) -> DownloadResult {
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if let Ok(result) = serde_json::from_str::<DownloadResult>(stdout.trim()) {
        return result;
    }

    DownloadResult {
        success: output.status.success(),
        message: if output.status.success() {
            stdout
        } else {
            stderr
        },
    }
}

#[tauri::command]
fn download_album(
    album_id: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let resource_path = app
        .path_resolver()
        .resolve_resource("dist/jmcomic-bridge")
        .ok_or("Failed to resolve resource path")?;
    let mut cmd = Command::new(&resource_path);
    cmd.arg("download").arg(&album_id);
    if let Some(dir) = save_dir {
        cmd.arg(&dir);
    }
    let output = cmd.output().map_err(|e| e.to_string())?;

    Ok(parse_download_output(output))
}

#[tauri::command]
fn download_chapter(
    chapter_id: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let resource_path = app
        .path_resolver()
        .resolve_resource("dist/jmcomic-bridge")
        .ok_or("Failed to resolve resource path")?;
    let mut cmd = Command::new(&resource_path);
    cmd.arg("download_chapter").arg(&chapter_id);
    if let Some(dir) = save_dir {
        cmd.arg(&dir);
    }
    let output = cmd.output().map_err(|e| e.to_string())?;

    Ok(parse_download_output(output))
}

#[tauri::command]
fn view_album(album_id: String, app: tauri::AppHandle) -> Result<String, String> {
    let resource_path = app
        .path_resolver()
        .resolve_resource("dist/jmcomic-bridge")
        .ok_or("Failed to resolve resource path")?;
    let output = Command::new(&resource_path)
        .arg("view")
        .arg(&album_id)
        .output()
        .map_err(|e| e.to_string())?;

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            download_album,
            download_chapter,
            view_album
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
