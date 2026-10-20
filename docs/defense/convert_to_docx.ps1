$htmlPath = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\SWE3004_Review2_Report_ShelfLife.html"
$docxPath = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\SWE3004_Review2_Report_ShelfLife.docx"

Write-Host "Starting Word COM conversion..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($htmlPath)
    # 16 = wdFormatDocumentDefault (.docx)
    $doc.SaveAs([ref]$docxPath, [ref]16)
    $doc.Close()
    Write-Host "[SUCCESS] Exported DOCX to: $docxPath"
}
catch {
    Write-Error $_.Exception.Message
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
