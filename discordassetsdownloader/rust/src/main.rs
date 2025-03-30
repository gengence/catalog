use reqwest::blocking::get;
use reqwest::Error;
use regex::Regex;
use std::fs::{self, File};
use std::io::{self, BufRead, Write};
use std::path::{Path, PathBuf};

fn sanitize_filename(filename: &str) -> String {
    let valid_filename = filename.replace(&['<', '>', ':', '"', '/', '\\', '|', '?', '*'][..], "");
    valid_filename.chars().take(255).collect()
}

fn get_unique_filename(directory: &Path, filename: &str) -> PathBuf {
    let base_name = Path::new(filename).file_stem().unwrap().to_string_lossy().to_string();
    let extension = Path::new(filename).extension().unwrap_or_default();
    let mut counter = 1;
    let mut unique_filename = filename.to_string();
    let mut path = directory.join(&unique_filename);

    while path.exists() {
        unique_filename = format!("{}-{}.{}", base_name, counter, extension.to_string_lossy());
        path = directory.join(&unique_filename);
        counter += 1;
    }

    path
}

fn download_discord_attachments_from_folder(folder_path: &str, download_folder: &str) -> io::Result<()> {
    let download_path = Path::new(download_folder);
    if !download_path.exists() {
        fs::create_dir_all(download_path)?;
    }

    let url_pattern = Regex::new(r"https://(?:cdn\.discordapp\.com|media\.discordapp\.net)/attachments/\S+").unwrap();

    for entry in fs::read_dir(folder_path)? {
        let entry = entry?;
        let file_path = entry.path();

        if file_path.extension().map_or(false, |ext| ext == "txt") {
            let subdirectory_name = sanitize_filename(file_path.file_stem().unwrap().to_str().unwrap());
            let subdirectory_path = download_path.join(&subdirectory_name);
            if !subdirectory_path.exists() {
                fs::create_dir_all(&subdirectory_path)?;
            }

            let file = File::open(&file_path)?;
            for line in io::BufReader::new(file).lines() {
                let line = line?;
                for url in url_pattern.find_iter(&line) {
                    if let Err(e) = download_and_save_file(&url.as_str(), &subdirectory_path) {
                        eprintln!("Failed to download {} from {}: {}", url.as_str(), file_path.display(), e);
                    }
                }
            }
        }
    }
    Ok(())
}

fn download_and_save_file(url: &str, directory: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let response = get(url)?;
    response.error_for_status_ref()?;

    let file_name = sanitize_filename(Path::new(url).file_name().unwrap().to_str().unwrap());
    let unique_file_path = get_unique_filename(directory, &file_name);

    let mut file = File::create(unique_file_path).map_err(|e| format!("IO error: {}", e))?;
    file.write_all(&response.bytes()?).map_err(|e| format!("IO error: {}", e))?;

    println!("Downloaded: {} from {}", file_name, url);
    Ok(())
}

fn main() -> io::Result<()> {
    let folder_with_txt_files = "";  // Replace with the path to your folder containing text files
    let download_directory = "";    // Replace with your desired download folder

    download_discord_attachments_from_folder(folder_with_txt_files, download_directory)
}
