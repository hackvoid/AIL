$scriptDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($scriptDir)) { $scriptDir = ".\" }

# Check if the system recognizes the global FFmpeg command
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: The terminal has not loaded FFmpeg into the PATH yet." -ForegroundColor Red
    Write-Host "Action Required: Close this entire PowerShell window, open a new one, and run the script again." -ForegroundColor Yellow
    exit
}

$videoFiles = Get-ChildItem -Path $scriptDir -File | Where-Object { $_.Extension -in '.mp4', '.mkv' }

if ($videoFiles.Count -eq 0) {
    Write-Host "No .mp4 or .mkv files found in the directory." -ForegroundColor Yellow
    exit
}

Write-Host "Found $($videoFiles.Count) files. Converting to speech-optimized MP3s..." -ForegroundColor Cyan

foreach ($file in $videoFiles) {
    $inputFile = $file.FullName
    $outputFile = [System.IO.Path]::ChangeExtension($inputFile, ".mp3")
    $outputFileName = Split-Path $outputFile -Leaf
    
    Write-Host "`nConverting: $($file.Name) -> $outputFileName" -ForegroundColor Blue
    
    # -ac 1 downmixes to mono, -b:a 64k sets an optimal bitrate for speech
    & ffmpeg -i $inputFile -vn -acodec libmp3lame -ac 1 -b:a 64k $outputFile -y
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully converted: $outputFileName" -ForegroundColor Green
    } else {
        Write-Host "Error converting: $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "`nAll conversions complete!" -ForegroundColor Cyan