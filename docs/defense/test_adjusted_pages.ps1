param([string]$path = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\test_expanded.docx")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($path)
    foreach ($p in $doc.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        if ($txt -like "*CHAPTER 1*") {
            $adj = $p.Range.Information(1) # wdActiveEndAdjustedPageNumber = 1
            $abs = $p.Range.Information(3) # wdActiveEndPageNumber = 3
            Write-Host "CHAPTER 1 => Adjusted Page: $adj | Absolute Page: $abs"
            break
        }
    }
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
