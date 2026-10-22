$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\SWE3004_Final_Project_Report_ShelfLife.docx')
    Write-Host "Total Paragraphs: $($doc.Paragraphs.Count)"
    foreach ($p in $doc.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        if ($txt -match "^CHAPTER \d" -or $txt -match "^REFERENCES") {
            $pageNum = $p.Range.Information(3) # 3 = wdActiveEndPageNumber
            Write-Host "$txt -> Page $pageNum"
        }
    }
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
