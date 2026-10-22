param([string]$path = "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense\SWE3004_Final_Project_Report_ShelfLife.docx")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($path)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Total Document Pages: $pages"
    
    $targets = @(
        "CHAPTER 1",
        "1.1 Objective",
        "1.2 Motivation",
        "1.3 Background",
        "CHAPTER 2",
        "2.1 LITERATURE SURVEY",
        "2.2 Project Overview",
        "2.3 Problem Statement",
        "2.4 Project Objectives",
        "2.5 Scope of the Project",
        "2.6 Existing System",
        "2.7 Proposed System",
        "CHAPTER 3",
        "3.1 Hardware Requirements",
        "3.2 Software Requirements",
        "3.3 Technologies and Tools Used",
        "3.4 Dataset and Retail Store Domain",
        "3.5 System Requirements",
        "CHAPTER 4",
        "4.1 Design Approach / Materials and Methods",
        "4.2 System Architecture",
        "4.3 Data Preprocessing and Feature Engineering",
        "4.4 Supervised Demand Forecasting Model",
        "4.5 Spoilage Risk Probability Classifier",
        "4.6 Multi-Batch FEFO Allocation and Dynamic Clearance Markdown Model",
        "4.7 Web Dashboard & Point-of-Sale System Design",
        "4.8 Codes and Standards",
        "4.9 Constraints, Alternatives and Trade-offs",
        "CHAPTER 5",
        "5.1 Project Planning",
        "5.2 Task Breakdown",
        "5.3 Project Timeline",
        "5.4 Milestones Achieved",
        "CHAPTER 6",
        "6.1 System Workflow",
        "6.2 Demand Forecasting Implementation",
        "6.3 Spoilage Risk Engine Implementation",
        "6.4 Dynamic Clearance Markdown and FEFO Implementation",
        "6.5 Web Dashboard and Point-of-Sale Implementation",
        "6.6 Dashboard Features and Demonstration Walkthrough",
        "CHAPTER 7",
        "7.1 Demand Forecasting Results",
        "7.2 Spoilage Classification Results",
        "7.3 Dynamic Markdown and Capital Salvage Results",
        "7.4 Dashboard Results and Retail Statistics",
        "7.5 Discussion and Limitations",
        "7.6 Sample Code",
        "CHAPTER 8",
        "8.1 Summary",
        "8.2 Major Findings",
        "8.3 Major Contributions",
        "8.4 Recommendations",
        "8.5 Future Scope",
        "8.6 Final Conclusion",
        "REFERENCES"
    )

    $figTargets = @(
        "Fig. 4.1", "Fig. 4.2", "Fig. 4.3", "Fig. 5.1",
        "Fig. 6.1", "Fig. 6.2", "Fig. 6.3", "Fig. 6.4", "Fig. 6.5",
        "Fig. 7.1", "Fig. 7.2"
    )

    $tblTargets = @(
        "Table 2.1", "Table 2.2", "Table 3.1", "Table 3.2", "Table 3.3",
        "Table 3.4", "Table 3.5", "Table 4.3", "Table 5.1", "Table 5.2",
        "Table 7.1", "Table 7.2", "Table 7.3", "Table 7.4", "Table 7.5", "Table 7.6"
    )

    $sec2 = $doc.Sections.Item(2)
    Write-Host "--- SECTION 2 (BODY) EXACT HEADINGS ---"
    foreach ($t in $targets) {
        $found = $false
        foreach ($p in $sec2.Range.Paragraphs) {
            $txt = $p.Range.Text.Trim()
            if ($txt.StartsWith($t)) {
                $adj = $p.Range.Information(1)
                Write-Host "$t => $adj"
                $found = $true
                break
            }
        }
        if (-not $found) {
            Write-Host "$t => NOT FOUND"
        }
    }

    Write-Host "`n--- SECTION 2 (BODY) EXACT FIGURES ---"
    foreach ($f in $figTargets) {
        foreach ($p in $sec2.Range.Paragraphs) {
            $txt = $p.Range.Text.Trim()
            if ($txt.StartsWith($f)) {
                $adj = $p.Range.Information(1)
                Write-Host "$f => $adj"
                break
            }
        }
    }

    Write-Host "`n--- SECTION 2 (BODY) EXACT TABLES ---"
    foreach ($tb in $tblTargets) {
        foreach ($p in $sec2.Range.Paragraphs) {
            $txt = $p.Range.Text.Trim()
            if ($txt.StartsWith($tb)) {
                $adj = $p.Range.Information(1)
                Write-Host "$tb => $adj"
                break
            }
        }
    }

    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
