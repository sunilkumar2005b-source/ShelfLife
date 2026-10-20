$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docxPath = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\SWE3004_Review2_Report_ShelfLife.docx"
    $doc = $word.Documents.Open($docxPath)
    Write-Host "File verified successfully!"
    Write-Host "Paragraphs Count: " $doc.Paragraphs.Count
    Write-Host "Tables Count:     " $doc.Tables.Count
    Write-Host "Words Count:      " $doc.Words.Count
    Write-Host "Pages Count:      " $doc.ComputeStatistics(2)
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
