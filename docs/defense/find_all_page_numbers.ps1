param([string]$path = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\test_expanded.docx")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($path)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Total Document Pages: $pages"
    
    Write-Host "`n=== DETECTED HEADINGS & PAGES ==="
    foreach ($p in $doc.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        if ($txt -match "^(CHAPTER \d|REFERENCES|\d+\.\d+|\bAcknowledgement\b|\bExecutive Summary\b|\bCONTENTS\b|\bList of Figures\b|\bList of Tables\b|\bList of Abbreviations\b|\bSymbols and Notations\b)") {
            # wdActiveEndAdjustedPageNumber = 3
            # wdActiveEndPageNumber = 3
            $pg = $p.Range.Information(3)
            # In section 2, check section page number
            $sec = $p.Range.Sections.Item(1)
            $secIndex = $doc.Sections.Index
            Write-Host "$txt ===> Page: $pg"
        }
        if ($txt -match "^(Fig\.|Figure|Table)") {
            $pg = $p.Range.Information(3)
            Write-Host "CAPTION: $txt ===> Page: $pg"
        }
    }
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
