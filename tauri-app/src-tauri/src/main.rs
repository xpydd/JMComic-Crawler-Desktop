#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::{Command, Output};

#[cfg(target_os = "windows")]
const BRIDGE_RESOURCE: &str = "../../tauri-app/dist/jmcomic-bridge.exe";

#[cfg(not(target_os = "windows"))]
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

async fn run_bridge(app: tauri::AppHandle, args: Vec<String>) -> Result<Output, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let resource_path = bridge_resource_path(&app)?;
        let mut cmd = Command::new(&resource_path);
        cmd.args(args);
        cmd.output().map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| e.to_string())?
}

fn push_save_dir_arg(args: &mut Vec<String>, save_dir: Option<String>) {
    if let Some(dir) = save_dir.filter(|dir| !dir.trim().is_empty()) {
        args.push(dir);
    }
}

#[tauri::command]
async fn download_album(
    album_id: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let mut args = vec!["download".to_string(), album_id];
    push_save_dir_arg(&mut args, save_dir);
    let output = run_bridge(app, args).await?;

    Ok(parse_download_output(output))
}

#[tauri::command]
async fn download_chapter(
    chapter_id: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let mut args = vec!["download_chapter".to_string(), chapter_id];
    push_save_dir_arg(&mut args, save_dir);
    let output = run_bridge(app, args).await?;

    Ok(parse_download_output(output))
}

#[tauri::command]
async fn download_chapters(
    chapter_ids: String,
    save_dir: Option<String>,
    app: tauri::AppHandle,
) -> Result<DownloadResult, String> {
    let mut args = vec!["download_chapters".to_string(), chapter_ids];
    push_save_dir_arg(&mut args, save_dir);
    let output = run_bridge(app, args).await?;

    Ok(parse_download_output(output))
}

#[tauri::command]
async fn view_album(album_id: String, app: tauri::AppHandle) -> Result<String, String> {
    let output = run_bridge(app, vec!["view".to_string(), album_id]).await?;

    Ok(parse_view_output(output))
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
            view_album
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
