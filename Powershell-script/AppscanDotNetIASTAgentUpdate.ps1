# Replace destinationPath with the path where your appscan agent nuget file is
$destinationPath = "C:\Users\ziv.riechman\Desktop\Kub Net\"
$headers = @{
    'accept' = 'application/json'
}

$url = "https://cloud.appscan.com/api/v4/Tools/IastAgent?type=DotNet"


# Donwload the file
$response = curl -Uri $url -Method 'GET' -Headers $headers

# Get the original name of the file
$content = [System.Net.Mime.ContentDisposition]::new($response.Headers["Content-Disposition"])
$fileName = $content.FileName

# Check if the latest version already exists in the directory
if (-not (Test-Path -Path (Join-Path -Path $destinationPath -ChildPath $fileName))) {

    # Get all files in the directory that start with "com.HCL.AppScan.IAST.agent" and have the extension .nupkg
    $nupkgFiles = Get-ChildItem -Path $destinationPath -Filter "com.HCL.AppScan.IAST.agent*.nupkg" -File
    # Filter the files based on the last write time and select the last modified file
    $oldAgentgFile = $nupkgFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $oldAgentPath = Join-Path -Path $destinationPath -ChildPath $oldAgentgFile

    # Create path with the file name that was downloaded and the path we defined before ($destinationPath)
    $newAgentPath = Join-Path -Path $destinationPath -ChildPath $fileName
    $file = [System.IO.FileStream]::new($newAgentPath, [System.IO.FileMode]::Create)

    # Write the file to the disk
    $file.Write($response.Content, 0, $response.RawContentLength)
    $file.Close()

    $tempExtractPathOld = Join-Path -Path $destinationPath -ChildPath "Previous version"
    $tempExtractPathNew = Join-Path -Path $destinationPath -ChildPath "Latest version"

    $oldAgentZipPath = $oldAgentPath -replace '\.nupkg$', '.zip'
    $newAgentZipPath = $newAgentPath -replace '\.nupkg$', '.zip'

    # Rename .nupkg with .zip
    Rename-Item -Path $oldAgentPath -NewName $oldAgentZipPath
    Rename-Item -Path $newAgentPath -NewName $newAgentZipPath

    # Exapnd .zip files
    Expand-Archive -Path $oldAgentZipPath -DestinationPath $tempExtractPathOld -Force
    Expand-Archive -Path $newAgentZipPath -DestinationPath $tempExtractPathNew -Force

    # Copy config files from older version to the new one
    $coreConfigFilePath = "iastConfig\asoc-config.json"
    $fwConfigDirPath = "content"
    Copy-Item -Path (Join-Path -Path $tempExtractPathOld -ChildPath $coreConfigFilePath) -Destination (Join-Path -Path $tempExtractPathNew -ChildPath $coreConfigFilePath) -Force -Confirm:$false
    Copy-Item -Path (Join-Path -Path $tempExtractPathOld -ChildPath $fwConfigDirPath) -Destination $tempExtractPathNew -Recurse -Force -Confirm:$false

    # Recompress the new package with the updated asoc-config.json
    Compress-Archive -Path $tempExtractPathNew\* -DestinationPath $newAgentZipPath -Force

    # Rename back to .nupkg extension
    Rename-Item -Path $newAgentZipPath -NewName $newAgentPath
    Rename-Item -Path $oldAgentZipPath -NewName $oldAgentPath

    # Remove tmp folders
    Remove-Item -Path $tempExtractPathOld -Recurse -Force
    Remove-Item -Path $tempExtractPathNew -Recurse -Force

}