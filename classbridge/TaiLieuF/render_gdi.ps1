Add-Type -AssemblyName System.Drawing

$jsonPath = "d:\TailieuNPKH\classbridge\TaiLieuF\02_HinhAnh_SoDo_PNG\diagrams_render_spec.json"
$rawJson = [System.IO.File]::ReadAllText($jsonPath, [System.Text.Encoding]::UTF8)
$diagrams = $rawJson | ConvertFrom-Json

function New-RoundedRectPath([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    if ($r -le 0.5) {
        $path.AddRectangle((New-Object System.Drawing.RectangleF($x, $y, $w, $h)))
        return $path
    }
    $d = $r * 2.0
    if ($d -gt $w) { $d = $w }
    if ($d -gt $h) { $d = $h }
    $path.AddArc($x, $y, $d, $d, 180, 90)
    $path.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $path.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $path.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    return $path
}

function New-FolderPath([float]$x, [float]$y, [float]$w, [float]$h, [float]$tabW, [float]$tabH, [float]$r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    # Top-left folder tab
    $path.AddLine($x, ($y + $tabH), $x, ($y + 3))
    $path.AddLine($x, ($y + 3), ($x + 3), $y)
    $path.AddLine(($x + 3), $y, ($x + $tabW - 6), $y)
    $path.AddLine(($x + $tabW - 6), $y, ($x + $tabW), ($y + $tabH))
    # Main folder box
    $path.AddLine(($x + $tabW), ($y + $tabH), ($x + $w), ($y + $tabH))
    $path.AddLine(($x + $w), ($y + $tabH), ($x + $w), ($y + $h))
    $path.AddLine(($x + $w), ($y + $h), $x, ($y + $h))
    $path.CloseFigure()
    return $path
}

$scale = 1.5
$fontFamily = New-Object System.Drawing.FontFamily("Segoe UI")
$fontMono = New-Object System.Drawing.FontFamily("Consolas")
$fontTitle = New-Object System.Drawing.Font($fontFamily, [float](13.0 * $scale), [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$fontStereo = New-Object System.Drawing.Font($fontFamily, [float](10.0 * $scale), [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$fontBody = New-Object System.Drawing.Font($fontFamily, [float](11.2 * $scale), [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$fontTerminal = New-Object System.Drawing.Font($fontMono, [float](12.5 * $scale), [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$fontBoundaryTitle = New-Object System.Drawing.Font($fontFamily, [float](13.5 * $scale), [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$fontBoundarySub = New-Object System.Drawing.Font($fontFamily, [float](10.5 * $scale), [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$fontEdge1 = New-Object System.Drawing.Font($fontFamily, [float](10.6 * $scale), [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$fontEdge2 = New-Object System.Drawing.Font($fontFamily, [float](9.8 * $scale), [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)

$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center

$sfLeft = New-Object System.Drawing.StringFormat
$sfLeft.Alignment = [System.Drawing.StringAlignment]::Near
$sfLeft.LineAlignment = [System.Drawing.StringAlignment]::Near

foreach ($diag in $diagrams) {
    $W = [int]($diag.canvas_w * $scale)
    $H = [int]($diag.canvas_h * $scale)
    $bmp = New-Object System.Drawing.Bitmap($W, $H)
    $bmp.SetResolution(220, 220)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.Clear([System.Drawing.Color]::White)

    # 1. Draw Boundaries (c4model.com style: rounded grey frame + title at BOTTOM-LEFT)
    foreach ($b in $diag.boundaries) {
        $bx = [float]($b.x * $scale)
        $by = [float]($b.y * $scale)
        $bw = [float]($b.w * $scale)
        $bh = [float]($b.h * $scale)

        $bPath = New-RoundedRectPath $bx $by $bw $bh (10 * $scale)
        $bPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(90, 98, 106), [float](2.2 * $scale))
        $g.DrawPath($bPen, $bPath)

        # Boundary Title & Subtitle at Bottom-Left inside the boundary frame
        $bTitleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(40, 48, 56))
        $bSubBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(95, 105, 115))
        $g.DrawString($b.title, $fontBoundaryTitle, $bTitleBrush, ($bx + 14 * $scale), ($by + $bh - 38 * $scale), $sfLeft)
        $g.DrawString($b.subtitle, $fontBoundarySub, $bSubBrush, ($bx + 14 * $scale), ($by + $bh - 20 * $scale), $sfLeft)
    }

    # 2. Draw Straight Dashed Arrows (c4model.com style)
    $edgePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(105, 115, 125), [float](1.9 * $scale))
    $edgePen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Custom
    $edgePen.DashPattern = @([float]4.2, [float]3.2)
    $arrowCap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap([float](5.2), [float](6.2), $true)
    $edgePen.CustomEndCap = $arrowCap

    foreach ($e in $diag.edges) {
        $pts = New-Object 'System.Collections.Generic.List[System.Drawing.PointF]'
        foreach ($pt in $e.points) {
            $pts.Add((New-Object System.Drawing.PointF([float]($pt[0] * $scale), [float]($pt[1] * $scale))))
        }
        if ($pts.Count -ge 2) {
            $g.DrawLines($edgePen, $pts.ToArray())
        }
    }

    # 3. Draw Nodes (Exact c4model.com visual shapes!)
    foreach ($n in $diag.nodes) {
        $nx = [float]($n.x * $scale)
        $ny = [float]($n.y * $scale)
        $nw = [float]($n.w * $scale)
        $nh = [float]($n.h * $scale)
        $kind = $n.kind

        # Default colors (Blue Container/Component inside boundary)
        $fillCol = [System.Drawing.Color]::FromArgb(242, 247, 252)
        $strokeCol = [System.Drawing.Color]::FromArgb(59, 105, 152)
        $titleCol = [System.Drawing.Color]::FromArgb(26, 62, 102)
        $stereoCol = [System.Drawing.Color]::FromArgb(75, 105, 138)
        $bodyCol = [System.Drawing.Color]::FromArgb(30, 58, 92)
        $strokeW = [float](2.2 * $scale)

        if ($kind -eq "person") {
            # C4 Person: Green outline + Head circle on top + Rounded-shoulder torso underneath
            $fillCol = [System.Drawing.Color]::FromArgb(245, 251, 247)
            $strokeCol = [System.Drawing.Color]::FromArgb(59, 118, 84)
            $titleCol = [System.Drawing.Color]::FromArgb(30, 74, 49)
            $stereoCol = [System.Drawing.Color]::FromArgb(68, 112, 86)
            $bodyCol = [System.Drawing.Color]::FromArgb(35, 78, 53)

            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)

            $headR = [float](24 * $scale)
            $headCx = $nx + $nw / 2.0
            $headCy = $ny + $headR + 2 * $scale

            $torsoY = $ny + $headR * 1.85
            $torsoH = $nh - ($headR * 1.85)
            $torsoPath = New-RoundedRectPath $nx $torsoY $nw $torsoH (30 * $scale)
            $g.FillPath($fillBrush, $torsoPath)
            $g.DrawPath($nodePen, $torsoPath)

            # Draw head circle above torso
            $g.FillEllipse($fillBrush, ($headCx - $headR), ($headCy - $headR), ($headR * 2.0), ($headR * 2.0))
            $g.DrawEllipse($nodePen, ($headCx - $headR), ($headCy - $headR), ($headR * 2.0), ($headR * 2.0))

            $textStartY = $torsoY + 12 * $scale
        }
        elseif ($kind -eq "ui") {
            # C4 Browser Window Container: Blue box + Browser top bar + 3 dots + URL bar
            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)

            $uPath = New-RoundedRectPath $nx $ny $nw $nh (6 * $scale)
            $g.FillPath($fillBrush, $uPath)
            $g.DrawPath($nodePen, $uPath)

            $barH = [float](22 * $scale)
            $g.DrawLine($nodePen, $nx, ($ny + $barH), ($nx + $nw), ($ny + $barH))

            # 3 browser dots on top-left
            $dotD = [float](6.5 * $scale)
            $dotY = $ny + ($barH - $dotD) / 2.0
            for ($di = 0; $di -lt 3; $di++) {
                $dotX = $nx + (10 + $di * 11) * $scale
                $g.DrawEllipse($nodePen, $dotX, $dotY, $dotD, $dotD)
            }
            # URL bar on top-right
            $urlX = $nx + 46 * $scale
            $urlW = $nw - 54 * $scale
            $urlH = [float](9 * $scale)
            $urlY = $ny + ($barH - $urlH) / 2.0
            $urlPen = New-Object System.Drawing.Pen($strokeCol, [float](1.4 * $scale))
            $g.DrawRectangle($urlPen, $urlX, $urlY, $urlW, $urlH)

            $textStartY = $ny + $barH + 10 * $scale
        }
        elseif ($kind -eq "folder") {
            # C4 Folder Component: Top-left tab + Rectangle body
            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)
            $tabW = [float](76 * $scale)
            $tabH = [float](15 * $scale)

            $fPath = New-FolderPath $nx $ny $nw $nh $tabW $tabH (4 * $scale)
            $g.FillPath($fillBrush, $fPath)
            $g.DrawPath($nodePen, $fPath)
            $g.DrawLine($nodePen, $nx, ($ny + $tabH), ($nx + $tabW), ($ny + $tabH))

            $textStartY = $ny + $tabH + 10 * $scale
        }
        elseif ($kind -eq "backend" -or $kind -eq "comp" -or $kind -eq "sys") {
            # C4 Backend / Service Container: Blue box with ">_" terminal icon in top-left corner
            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)

            $bPath = New-RoundedRectPath $nx $ny $nw $nh (6 * $scale)
            $g.FillPath($fillBrush, $bPath)
            $g.DrawPath($nodePen, $bPath)

            if ($kind -eq "backend") {
                $termBrush = New-Object System.Drawing.SolidBrush($strokeCol)
                $g.DrawString(">_", $fontTerminal, $termBrush, ($nx + 8 * $scale), ($ny + 6 * $scale), $sfLeft)
            }
            $textStartY = $ny + 16 * $scale
        }
        elseif ($kind -eq "db") {
            # C4 Database / Cache Cylinder
            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)

            $capH = [float](20 * $scale)
            $bodyRect = New-Object System.Drawing.RectangleF($nx, ($ny + $capH / 2.0), $nw, ($nh - $capH))
            $g.FillRectangle($fillBrush, $bodyRect)
            $g.FillEllipse($fillBrush, $nx, ($ny + $nh - $capH), $nw, $capH)
            $g.DrawArc($nodePen, $nx, ($ny + $nh - $capH), $nw, $capH, 0, 180)
            $g.DrawLine($nodePen, $nx, ($ny + $capH / 2.0), $nx, ($ny + $nh - $capH / 2.0))
            $g.DrawLine($nodePen, ($nx + $nw), ($ny + $capH / 2.0), ($nx + $nw), ($ny + $nh - $capH / 2.0))
            $g.FillEllipse($fillBrush, $nx, $ny, $nw, $capH)
            $g.DrawEllipse($nodePen, $nx, $ny, $nw, $capH)

            $textStartY = $ny + $capH + 8 * $scale
        }
        elseif ($kind -eq "iface") {
            # Dashed Interface box
            $fillCol = [System.Drawing.Color]::White
            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)
            $nodePen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Custom
            $nodePen.DashPattern = @([float]4.5, [float]3.0)

            $iPath = New-RoundedRectPath $nx $ny $nw $nh (6 * $scale)
            $g.FillPath($fillBrush, $iPath)
            $g.DrawPath($nodePen, $iPath)
            $textStartY = $ny + 16 * $scale
        }
        else {
            # External System / Isolated Worker outside boundary (Warm brown-gray like c4model.com)
            $fillCol = [System.Drawing.Color]::FromArgb(248, 246, 246)
            $strokeCol = [System.Drawing.Color]::FromArgb(110, 92, 88)
            $titleCol = [System.Drawing.Color]::FromArgb(62, 46, 42)
            $stereoCol = [System.Drawing.Color]::FromArgb(110, 92, 88)
            $bodyCol = [System.Drawing.Color]::FromArgb(68, 52, 48)

            $fillBrush = New-Object System.Drawing.SolidBrush($fillCol)
            $nodePen = New-Object System.Drawing.Pen($strokeCol, $strokeW)

            $ePath = New-RoundedRectPath $nx $ny $nw $nh (8 * $scale)
            $g.FillPath($fillBrush, $ePath)
            $g.DrawPath($nodePen, $ePath)
            $textStartY = $ny + 16 * $scale
        }

        # Node Text: Title, [Stereotype], and Description Lines (Clean, no horizontal divider line, just like c4model.com!)
        $tBrush = New-Object System.Drawing.SolidBrush($titleCol)
        $sBrush = New-Object System.Drawing.SolidBrush($stereoCol)
        $bBrush = New-Object System.Drawing.SolidBrush($bodyCol)

        $rectTitle = New-Object System.Drawing.RectangleF(($nx + 8 * $scale), $textStartY, ($nw - 16 * $scale), (20 * $scale))
        $g.DrawString($n.title, $fontTitle, $tBrush, $rectTitle, $sfCenter)

        $stereoY = $textStartY + 18 * $scale
        $rectStereo = New-Object System.Drawing.RectangleF(($nx + 8 * $scale), $stereoY, ($nw - 16 * $scale), (16 * $scale))
        $g.DrawString($n.stereo, $fontStereo, $sBrush, $rectStereo, $sfCenter)

        $lineY = $stereoY + 21 * $scale
        $lineStep = [float](17.5 * $scale)
        foreach ($line in $n.lines) {
            $rectLine = New-Object System.Drawing.RectangleF(($nx + 8 * $scale), $lineY, ($nw - 16 * $scale), $lineStep)
            $g.DrawString($line, $fontBody, $bBrush, $rectLine, $sfCenter)
            $lineY += $lineStep
        }
    }

    # 4. Draw Edge Labels (Borderless white backing on midpoint of dashed arrow, exact c4model.com style!)
    $lblBgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(242, 255, 255, 255))
    $lblBrush1 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(55, 65, 75))
    $lblBrush2 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(90, 100, 110))

    foreach ($e in $diag.edges) {
        $lx = [float]($e.lx * $scale)
        $ly = [float]($e.ly * $scale)
        $parts = $e.label -split "`n"
        $l1 = $parts[0]
        $l2 = if ($parts.Count -gt 1) { $parts[1] } else { "" }

        $sz1 = $g.MeasureString($l1, $fontEdge1)
        $maxW = $sz1.Width
        $boxH = $sz1.Height + 4 * $scale
        if ($l2 -ne "") {
            $sz2 = $g.MeasureString($l2, $fontEdge2)
            if ($sz2.Width -gt $maxW) { $maxW = $sz2.Width }
            $boxH += $sz2.Height - 2 * $scale
        }
        $boxW = $maxW + 8 * $scale
        $bx = $lx - $boxW / 2.0
        $by = $ly - $boxH / 2.0

        $lPath = New-RoundedRectPath $bx $by $boxW $boxH (4 * $scale)
        $g.FillPath($lblBgBrush, $lPath)

        if ($l2 -ne "") {
            $r1 = New-Object System.Drawing.RectangleF($bx, ($by + 1 * $scale), $boxW, $sz1.Height)
            $r2 = New-Object System.Drawing.RectangleF($bx, ($by + $sz1.Height - 1 * $scale), $boxW, ($boxH - $sz1.Height + 2 * $scale))
            $g.DrawString($l1, $fontEdge1, $lblBrush1, $r1, $sfCenter)
            $g.DrawString($l2, $fontEdge2, $lblBrush2, $r2, $sfCenter)
        }
        else {
            $r1 = New-Object System.Drawing.RectangleF($bx, $by, $boxW, $boxH)
            $g.DrawString($l1, $fontEdge1, $lblBrush1, $r1, $sfCenter)
        }
    }

    $bmp.Save($diag.filename, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "[OK] Rendered c4model.com style PNG: $($diag.filename)"
}
