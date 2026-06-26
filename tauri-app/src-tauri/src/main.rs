#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::Command;
use tauri::api::dialog::blocking::FileDialogBuilder;

const BRIDGE_RESOURCE: &str = "../../tauri-app/dist/jmcomic-bridge";

#[derive(Serialize, Deserialize)]
struct DownloadResult {
    success: bool,
    message: String,
}

fn parse_download_output(output: std::process::Output) -> DownloadResult {
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if let Some(json) = extract_json_line(&stdout) {
        if let Ok(result) = serde_json::from_str::<DownloadResult>(json) {
            return result;
        }
    }

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

fn extract_json_line(output: &str) -> Option<&str> {
    output
        .lines()
        .rev()
        .map(str::trim)
        .find(|line| line.starts_with('{') && line.ends_with('}'))
}

fn parse_view_output(output: std::process::Output) -> String {
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();

    if let Some(json) = extract_json_line(&stdout) {
        return json.to_string();
    }

    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    let message = if stderr.is_empty() {
        stdout.trim().to_string()
    } else {
        stderr
    };

    serde_json::json!({ "error": message }).to_string()
}

fn bridge_resource_path(app: &tauri::AppHandle) -> Result<std::path::PathBuf, String> {
    app.path_resolver()
        .resolve_resource(BRIDGE_RESOURCE)
        .ok_or_else(|| format!("Failed to resolve resource path: {}", BRIDGE_RESOURCE))
}

#[tauri::command]
fn download_album(
    album_id: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let resource_path = bridge_resource_path(&app)?;
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
    let resource_path = bridge_resource_path(&app)?;
    let mut cmd = Command::new(&resource_path);
    cmd.arg("download_chapter").arg(&chapter_id);
    if let Some(dir) = save_dir {
        cmd.arg(&dir);
    }
    let output = cmd.output().map_err(|e| e.to_string())?;

    Ok(parse_download_output(output))
}

#[tauri::command]
fn download_chapters(
    chapter_ids: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let resource_path = bridge_resource_path(&app)?;
    let mut cmd = Command::new(&resource_path);
    cmd.arg("download_chapters").arg(&chapter_ids);
    if let Some(dir) = save_dir {
        cmd.arg(&dir);
    }
    let output = cmd.output().map_err(|e| e.to_string())?;

    Ok(parse_download_output(output))
}

#[tauri::command]
fn view_album(album_id: String, app: tauri::AppHandle) -> Result<String, String> {
    let resource_path = bridge_resource_path(&app)?;
    let output = Command::new(&resource_path)
        .arg("view")
        .arg(&album_id)
        .output()
        .map_err(|e| e.to_string())?;

    Ok(parse_view_output(output))
}

#[tauri::command]
fn choose_save_dir() -> Option<String> {
    FileDialogBuilder::new()
        .pick_folder()
        .map(|path| path.to_string_lossy().to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::os::unix::process::ExitStatusExt;

    #[test]
    fn extracts_last_json_line_from_noisy_stdout() {
        let stdout = "[2026-06-26 15:19:34] log line\n{\"id\":\"350234\",\"title\":\"ok\"}\n";

        assert_eq!(
            extract_json_line(stdout),
            Some("{\"id\":\"350234\",\"title\":\"ok\"}")
        );
    }

    #[test]
    fn view_output_returns_error_json_when_bridge_has_no_json() {
        let output = std::process::Output {
            status: std::process::ExitStatus::from_raw(1),
            stdout: b"[2026-06-26] noisy log".to_vec(),
            stderr: b"bridge failed".to_vec(),
        };

        assert_eq!(
            parse_view_output(output),
            "{\"error\":\"bridge failed\"}"
        );
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            download_album,
            download_chapter,
            download_chapters,
            view_album,
            choose_save_dir
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
