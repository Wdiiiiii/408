param([string]$Root = 'E:\codex_0_pro\408')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Await($Operation, [Type]$Type) {
    $task = $asTask.MakeGenericMethod($Type).Invoke($null, @($Operation))
    $task.Wait()
    $task.Result
}
$language = New-Object Windows.Globalization.Language('zh-Hans-CN')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
$utf8 = New-Object System.Text.UTF8Encoding($false)
$pagesRoot = Join-Path $Root '工作底稿\pages'
$ocrRoot = Join-Path $Root '工作底稿\ocr'
[System.IO.Directory]::CreateDirectory($ocrRoot) | Out-Null
foreach ($dir in Get-ChildItem -LiteralPath $pagesRoot -Directory | Sort-Object Name) {
    $target = Join-Path $ocrRoot ($dir.Name + '.json')
    if (Test-Path -LiteralPath $target) { continue }
    $records = @()
    foreach ($img in Get-ChildItem -LiteralPath $dir.FullName -Filter '*.png' | Sort-Object Name) {
        $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($img.FullName)) ([Windows.Storage.StorageFile])
        $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lines = @($result.Lines | ForEach-Object { $_.Text })
        $records += [PSCustomObject]@{page=[int]$img.BaseName; text=($lines -join "`n")}
        $bitmap.Dispose()
        $stream.Dispose()
    }
    [System.IO.File]::WriteAllText($target, (ConvertTo-Json -InputObject $records -Depth 5), $utf8)
    Write-Output ($dir.Name + ' OCR complete: ' + $records.Count)
}
