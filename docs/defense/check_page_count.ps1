param([string]$path = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\test_expanded.docx")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($path)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Exact Word Page Count: $pages"
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
