from __future__ import annotations

import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


SLIDES = [
    {
        "title": "House Price Prediction Project",
        "bullets": [
            "Notebook-based machine learning project using California housing data",
            "Main goal: understand the data and prepare a reliable price prediction workflow",
            "Focus on simple explanation for a general audience",
        ],
    },
    {
        "title": "Objectives",
        "bullets": [
            "Analyze important housing features such as income, rooms, location, and population",
            "Predict median house value from historical housing data",
            "Identify patterns, missing values, outliers, and correlations before modeling",
            "Build a clean machine learning workflow with preprocessing and evaluation",
        ],
    },
    {
        "title": "Dataset Overview",
        "bullets": [
            "Dataset: California housing dataset with 20,640 rows and 10 columns",
            "Target variable: median_house_value",
            "Important features: longitude, latitude, total_rooms, total_bedrooms, population, households, median_income, ocean_proximity",
            "One categorical feature: ocean_proximity",
        ],
    },
    {
        "title": "ML Model",
        "bullets": [
            "Preprocessing plan: median imputation, one-hot encoding, and scaling for linear models",
            "Training setup: train/test split with reproducible random state",
            "Candidate models: Linear Regression, Ridge, Lasso, Random Forest, and HistGradientBoosting",
            "Evaluation metrics: RMSE, MAE, and R-squared",
        ],
    },
    {
        "title": "Architecture Diagram",
        "diagram": [
            "Housing CSV Data",
            "EDA and Cleaning",
            "Preprocessing",
            "Train/Test Split",
            "Model Training",
            "Evaluation",
            "Price Prediction",
        ],
        "footer": "Flow: raw dataset to cleaned features to trained model to predicted house price",
    },
]


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {slides}
</Types>
"""


ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Macintosh PowerPoint</Application>
  <Slides>5</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <MMClips>0</MMClips>
  <PresentationFormat>On-screen Show (4:3)</PresentationFormat>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""


CORE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>House Price Prediction Project</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-04-15T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-04-15T00:00:00Z</dcterms:modified>
</cp:coreProperties>
"""


PRESENTATION_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1" autoCompressPictures="0">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId2"/>
    <p:sldId id="257" r:id="rId3"/>
    <p:sldId id="258" r:id="rId4"/>
    <p:sldId id="259" r:id="rId5"/>
    <p:sldId id="260" r:id="rId6"/>
  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000" type="screen4x3"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>
"""


PRESENTATION_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide3.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide4.xml"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide5.xml"/>
</Relationships>
"""


SLIDE_MASTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Simple Master">
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="F7F4EC"/></a:solidFill>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr/>
    </p:spTree>
  </p:cSld>
  <p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="lt1"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="1" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle/>
    <p:bodyStyle/>
    <p:otherStyle/>
  </p:txStyles>
</p:sldMaster>
"""


SLIDE_MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""


SLIDE_LAYOUT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr/>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""


SLIDE_LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""


THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Simple Theme">
  <a:themeElements>
    <a:clrScheme name="Simple">
      <a:dk1><a:srgbClr val="1F2937"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="374151"/></a:dk2>
      <a:lt2><a:srgbClr val="F7F4EC"/></a:lt2>
      <a:accent1><a:srgbClr val="2F6B5A"/></a:accent1>
      <a:accent2><a:srgbClr val="C97B2A"/></a:accent2>
      <a:accent3><a:srgbClr val="5B8DEF"/></a:accent3>
      <a:accent4><a:srgbClr val="C14953"/></a:accent4>
      <a:accent5><a:srgbClr val="6B7280"/></a:accent5>
      <a:accent6><a:srgbClr val="111827"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink>
      <a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Simple Fonts">
      <a:majorFont>
        <a:latin typeface="Aptos Display"/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Aptos"/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Simple Format">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="accent1"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525"><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="lt2"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>
"""


def paragraph(text: str, level: int = 0, bullet: bool = False) -> str:
    bullet_xml = f'<a:pPr lvl="{level}"><a:buChar char="•"/></a:pPr>' if bullet else "<a:pPr/>"
    return (
        f"<a:p>{bullet_xml}<a:r><a:rPr lang=\"en-US\" sz=\"2200\" dirty=\"0\"/>"
        f"<a:t>{escape(text)}</a:t></a:r><a:endParaRPr lang=\"en-US\" sz=\"2200\" dirty=\"0\"/></a:p>"
    )


def title_box(title: str) -> str:
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="2" name="Title"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="457200" y="274320"/><a:ext cx="8229600" cy="914400"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
      <p:txBody>
        <a:bodyPr/>
        <a:lstStyle/>
        <a:p>
          <a:pPr/>
          <a:r>
            <a:rPr lang="en-US" sz="2800" b="1" dirty="0" smtClean="0"/>
            <a:t>{escape(title)}</a:t>
          </a:r>
          <a:endParaRPr lang="en-US" sz="2800" b="1" dirty="0"/>
        </a:p>
      </p:txBody>
    </p:sp>
    """


def bullet_box(bullets: list[str]) -> str:
    paragraphs = "".join(paragraph(item, bullet=True) for item in bullets)
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="3" name="Content"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="685800" y="1463040"/><a:ext cx="7772400" cy="4114800"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square"/>
        <a:lstStyle/>
        {paragraphs}
      </p:txBody>
    </p:sp>
    """


def diagram_box(steps: list[str], footer: str) -> str:
    shapes = []
    start_x = 480000
    y = 2100000
    width = 1080000
    gap = 180000
    for index, text in enumerate(steps, start=10):
        x = start_x + (index - 10) * (width + gap)
        shapes.append(
            f"""
            <p:sp>
              <p:nvSpPr>
                <p:cNvPr id="{index}" name="Diagram {index}"/>
                <p:cNvSpPr/>
                <p:nvPr/>
              </p:nvSpPr>
              <p:spPr>
                <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{width}" cy="720000"/></a:xfrm>
                <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
                <a:solidFill><a:srgbClr val="DCEFE7"/></a:solidFill>
                <a:ln w="12700"><a:solidFill><a:srgbClr val="2F6B5A"/></a:solidFill></a:ln>
              </p:spPr>
              <p:txBody>
                <a:bodyPr anchor="ctr" wrap="square"/>
                <a:lstStyle/>
                {paragraph(text)}
              </p:txBody>
            </p:sp>
            """
        )
        if index < 10 + len(steps) - 1:
            arrow_x = x + width
            shapes.append(
                f"""
                <p:cxnSp>
                  <p:nvCxnSpPr>
                    <p:cNvPr id="{index + 100}" name="Arrow {index}"/>
                    <p:cNvCxnSpPr/>
                    <p:nvPr/>
                  </p:nvCxnSpPr>
                  <p:spPr>
                    <a:xfrm><a:off x="{arrow_x}" y="{y + 330000}"/><a:ext cx="{gap}" cy="1"/></a:xfrm>
                    <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
                    <a:ln w="19050" cap="rnd">
                      <a:solidFill><a:srgbClr val="C97B2A"/></a:solidFill>
                      <a:tailEnd type="none"/>
                      <a:headEnd type="triangle"/>
                    </a:ln>
                  </p:spPr>
                </p:cxnSp>
                """
            )
    shapes.append(
        f"""
        <p:sp>
          <p:nvSpPr>
            <p:cNvPr id="99" name="Footer"/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="685800" y="5000000"/><a:ext cx="7772400" cy="720000"/></a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          </p:spPr>
          <p:txBody>
            <a:bodyPr wrap="square"/>
            <a:lstStyle/>
            {paragraph(footer)}
          </p:txBody>
        </p:sp>
        """
    )
    return "".join(shapes)


def slide_xml(slide: dict[str, object]) -> str:
    content = title_box(str(slide["title"]))
    if "bullets" in slide:
        content += bullet_box(list(slide["bullets"]))
    else:
        content += diagram_box(list(slide["diagram"]), str(slide["footer"]))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="F7F4EC"/></a:solidFill>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr/>
      {content}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


SLIDE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""


def build_pptx(output_path: Path) -> None:
    slide_overrides = "\n  ".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES.format(slides=slide_overrides))
        archive.writestr("_rels/.rels", ROOT_RELS)
        archive.writestr("docProps/app.xml", APP_XML)
        archive.writestr("docProps/core.xml", CORE_XML)
        archive.writestr("ppt/presentation.xml", PRESENTATION_XML)
        archive.writestr("ppt/_rels/presentation.xml.rels", PRESENTATION_RELS)
        archive.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        archive.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        archive.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)
        archive.writestr("ppt/theme/theme1.xml", THEME_XML)
        for index, slide in enumerate(SLIDES, start=1):
            archive.writestr(f"ppt/slides/slide{index}.xml", slide_xml(slide))
            archive.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", SLIDE_RELS)


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("house_price_prediction_presentation.pptx")
    build_pptx(output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
