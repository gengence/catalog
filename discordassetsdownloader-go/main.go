package main

import (
	"bufio"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func sanitizeFilename(filename string) string {
	re := regexp.MustCompile(`[<>:"/\\|?*]`)
	validFilename := re.ReplaceAllString(filename, "")
	if len(validFilename) > 255 {
		return validFilename[:255]
	}
	return validFilename
}

func getUniqueFilename(directory, filename string) string {
	baseName := strings.TrimSuffix(filename, filepath.Ext(filename))
	extension := filepath.Ext(filename)
	counter := 1
	uniqueFilename := filename

	for {
		_, err := os.Stat(filepath.Join(directory, uniqueFilename))
		if os.IsNotExist(err) {
			break
		}
		uniqueFilename = fmt.Sprintf("%s-%d%s", baseName, counter, extension)
		counter++
	}

	return uniqueFilename
}

func downloadDiscordAttachmentsFromFolder(folderPath, downloadFolder string) {
	if err := os.MkdirAll(downloadFolder, os.ModePerm); err != nil {
		fmt.Printf("Error creating download folder: %v\n", err)
		return
	}

	urlPattern := regexp.MustCompile(`https://(cdn\.discordapp\.com|media\.discordapp\.net)/attachments/\S+`)

	files, err := os.ReadDir(folderPath)
	if err != nil {
		fmt.Printf("Error reading folder: %v\n", err)
		return
	}

	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".txt") {
			filePath := filepath.Join(folderPath, file.Name())
			subdirectoryName := strings.TrimSuffix(file.Name(), filepath.Ext(file.Name()))
			subdirectoryPath := filepath.Join(downloadFolder, sanitizeFilename(subdirectoryName))

			if err := os.MkdirAll(subdirectoryPath, os.ModePerm); err != nil {
				fmt.Printf("Error creating subdirectory: %v\n", err)
				continue
			}

			processFile(filePath, subdirectoryPath, urlPattern)
		}
	}
}

func processFile(filePath, subdirectoryPath string, urlPattern *regexp.Regexp) {
	file, err := os.Open(filePath)
	if err != nil {
		fmt.Printf("Error opening file %s: %v\n", filePath, err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		urls := urlPattern.FindAllString(line, -1)
		for _, url := range urls {
			downloadFile(url, subdirectoryPath, filePath)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("Error reading file %s: %v\n", filePath, err)
	}
}

func downloadFile(url, subdirectoryPath, filePath string) {
	fileName := filepath.Base(url)

	fileName = strings.Split(fileName, "?")[0]

	fileName = sanitizeFilename(fileName)

	uniqueFileName := getUniqueFilename(subdirectoryPath, fileName)
	downloadPath := filepath.Join(subdirectoryPath, uniqueFileName)

	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("Failed to download %s from %s: %v\n", url, filePath, err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Failed to download %s from %s: HTTP status %d\n", url, filePath, resp.StatusCode)
		return
	}

	out, err := os.Create(downloadPath)
	if err != nil {
		fmt.Printf("Error creating file %s: %v\n", downloadPath, err)
		return
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		fmt.Printf("Error writing to file %s: %v\n", downloadPath, err)
		return
	}

	fmt.Printf("Downloaded: %s from %s\n", uniqueFileName, filePath)
}

func main() {
	folderWithTxtFiles := "" // Replace with the path to your folder containing text files
	downloadDirectory := ""  // Replace with your desired download folder
	downloadDiscordAttachmentsFromFolder(folderWithTxtFiles, downloadDirectory)
}
