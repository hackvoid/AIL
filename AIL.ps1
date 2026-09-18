$scriptDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($scriptDir)) { $scriptDir = ".\" }

# Check if the system recognizes the global FFmpeg command
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: The terminal has not loaded FFmpeg into the PATH yet." -ForegroundColor Red
    Write-Host "Action Required: Close this entire PowerShell window, open a new one, and run the script again." -ForegroundColor Yellow
    exit
}

# Search all subfolders for video files
$videoFiles = Get-ChildItem -Path $scriptDir -File -Recurse | Where-Object { $_.Extension -in '.mp4', '.mkv' }

if ($videoFiles.Count -eq 0) {
    Write-Host "No .mp4 or .mkv files found in the directory or subdirectories." -ForegroundColor Yellow
    exit
}

Write-Host "Found $($videoFiles.Count) files. Converting to MP3s and deleting originals..." -ForegroundColor Cyan

foreach ($file in $videoFiles) {
    $inputFile = $file.FullName
    $outputFile = [System.IO.Path]::ChangeExtension($inputFile, ".mp3")
    $outputFileName = Split-Path $outputFile -Leaf
    
    # Grab the name of the folder the file is currently sitting in for the console output
    $parentFolder = Split-Path $file.DirectoryName -Leaf
    
    Write-Host "`nProcessing: [$parentFolder] $($file.Name)" -ForegroundColor Blue
    
    # -ac 1 downmixes to mono, -b:a 64k sets an optimal bitrate for speech
    & ffmpeg -i $inputFile -vn -acodec libmp3lame -ac 1 -b:a 64k $outputFile -y
    
    # Safely check if the conversion worked BEFORE deleting the original
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully converted: $outputFileName" -ForegroundColor Green
        
        # Delete the original video file
        Remove-Item -Path $inputFile -Force
        Write-Host "Deleted original video: $($file.Name)" -ForegroundColor DarkGray
    } else {
        Write-Host "Error converting: $($file.Name). Original file was NOT deleted." -ForegroundColor Red
    }
}

Write-Host "`nAll conversions and cleanups complete!" -ForegroundColor Cyan