const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, PageNumber, Footer
} = require('docx');

const FONT = 'Calibri';
const border = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const tableBorders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };
const HEADER_FILL = 'F2F2F2';

const P = (text) => new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text, font: FONT, size: 22 })]
});
const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 180 },
  children: [new TextRun({ text, font: FONT, size: 32, bold: true })]
});
const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 280, after: 140 },
  children: [new TextRun({ text, font: FONT, size: 26, bold: true })]
});
const H3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 200, after: 100 },
  children: [new TextRun({ text, font: FONT, size: 22, bold: true })]
});
const BUL = (text) => new Paragraph({
  numbering: { reference: 'bul', level: 0 },
  spacing: { after: 60 },
  children: [new TextRun({ text, font: FONT, size: 22 })]
});

function cell(text, width, opts = {}) {
  return new TableCell({
    borders: tableBorders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    shading: opts.head ? { fill: HEADER_FILL, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    children: [new Paragraph({
      children: [new TextRun({
        text: text == null ? '' : String(text),
        font: FONT, size: 20, bold: !!opts.head
      })]
    })]
  });
}

function buildTable(widths, headers, rows) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => cell(h, widths[i], { head: true }))
      }),
      ...rows.map(r => new TableRow({
        children: r.map((c, i) => cell(c, widths[i]))
      }))
    ]
  });
}

// ===== COLUMN WIDTHS (all sum to 9360 DXA = US Letter content width) =====
const certW   = [900, 5300, 1300, 1860];   // Code | Full Name | Hours | Fee
const tinyCertW = [900, 5800, 2660];        // Code | Full Name | Fee   (used where Hours irrelevant)
const programW = [3600, 4100, 1660];        // Product | Notes | Fee
const bookW    = [5400, 2300, 1660];        // Title | Sub-cluster | Fee
const membW    = [3800, 3500, 2060];        // Tier | Audience | Fee
const openW    = [3200, 6160];

// ===== DATA =====

// Group 1 — Innovation Core
const ic_cip = [
  ['CIP-0', 'Certified Innovation Professional Level 0: Innovation Champion', '20h',     '$200'],
  ['CIP-1', 'Certified Innovation Professional Level 1: Associate',           '32-40h',  '$560'],
  ['CIP-2', 'Certified Innovation Professional Level 2: Master',              '32-40h',  '$560']
];
const ic_cip_mc = [
  ['—', 'CIP Masterclass (virtual cohort)', '$2,000']
];
const ic_ccio = [
  ['CCIO-1', 'Certified Chief Innovation Officer Level 3: Manager', '32-40h',  '$560'],
  ['CCIO-2', 'Certified Chief Innovation Officer Level 4: Leader',  '6 months','$560']
];
const ic_ccio_mc = [
  ['—', 'CCIO Masterclass (virtual cohort)', '$2,600']
];
const ic_impact = [
  ['CGIS-1', 'Certified GIMI Impact: Students', '12h', '$100'],
  ['CGIT',   'Certified GIMI Impact: Teachers', '12h', '$250']
];
const ic_trainer = [
  ['CGT', 'Certified GIMI Trainer', '8h', '$510']
];

// Group 2 — Innovation Elective
const elective = [
  ['IP',     'Innovation Primer',                            '2h',  'Free'],
  ['PBCC',   'Problem Solving Certified Catalyst',           '16h', '$200'],
  ['CDT-1',  'Certified Design Thinking: Level 1',           '32h', '$410'],
  ['CDT-2',  'Certified Design Thinking: Level 2',           '24h', '$410'],
  ['CDTT-3', 'Certified Design Thinking Trainer',            '40h', '$410'],
  ['CAAP',   'Certified AI Agent Practitioner',              '4h',  '$495'],
  ['CGA',    'Certified GIMI Auditor',                       '20h', '$2,000'],
  ['CIME',   'Certified ISO Innovation Management Expert',   '20h', '$1,200'],
  ['CTC',    'Certified Technology Catalyst',                '20h', '$200'],
  ['CLC',    'Certified Longevity Catalyst',                 '12h', '$200']
];

// Group 3 — Future Foresight
const ff_series = [
  ['CFF-1', 'Certified Foresight Professional: Level 1', 'TBD', '$560'],
  ['CFF-2', 'Certified Foresight Leader: Level 2',       'TBD', '$560'],
  ['CFF-3', 'Certified Foresight Officer: Level 3',      'TBD', '$560']
];
const ff_trainer = [
  ['CFF-4', 'Certified Trainer in Future Foresight Level 1', 'TBD', '$2,000'],
  ['CFF-5', 'Certified Trainer in Future Foresight Level 2', 'TBD', '$2,000']
];

// Group 4 — Leadership Core
const leadership = [
  ['CLF-1', 'Certified Leader for the Future', '24h',  '$510'],
  ['CIL',   'Certified Innovation Leader',     '1.5h', '$200']
];

// Group 5 — Consulting Core
const consulting = [
  ['MCI-1', 'Certified Management Consulting Level 1: Analyst',    '20h',      '$510'],
  ['MCI-2', 'Certified Management Consulting Level 2: Consultant', '30h',      '$510'],
  ['MCI-3', 'Certified Management Consulting Level 3: Manager',    '40h',      '$510'],
  ['MCI-4', 'Certified Management Consulting Level 4: Leader',     'Variable', '$510']
];

// Group 6 — Books & Guides
const books_imbok = [
  ['IMBOK Level 1 Guide',  'IMBOK', '$45'],
  ['IMBOK Level 3 Guide',  'IMBOK', '$45']
];
const books_ffbok = [
  ['Future Foresight Body of Knowledge – Level 1', 'FFBOK', '$45'],
  ['Future Foresight Body of Knowledge – Level 2', 'FFBOK', '$45']
];
const books_iso = [
  ['ISO Book – ISO 56000 Series',  'ISO Standards', '$50']
];
const books_stories = [
  ['Game Changers',  'Innovation Stories', '$20'],
  ['Connectivate!',  'Innovation Stories', '$20'],
  ['Healthovate!',   'Innovation Stories', '$20'],
  ['Greenovate!',    'Innovation Stories', '$20'],
  ['Squiggly Lines', 'Innovation Stories', '$25']
];
const books_tools = [
  ['GIMI iDeX – Ideation Techniques for Idea Excellence', 'Practitioner Tools', '$15'],
  ['Technovate (Book + App)',                             'Practitioner Tools', '$99']
];
const books_journal = [
  ['International Journal of Innovation Science', 'Journal', 'TBD']
];

// Group 7 — Programs & Tools
const pt_indiv = [
  ['IPA Individual',                              'Self-assessment, 45 min, automated report',                  '$50'],
  ['Innovation Mindset Index',                    'Online individual assessment',                                '$50'],
  ['GIMI Innovation Awards – Individual Ticket',  'Attendance ticket for the annual Awards ceremony',            '$400']
];
const pt_org = [
  ['IPA Corporate',
   'Team-level Innovation Potential Assessment; tiered by company/BU size',
   'from $5,000'],
  ['OIA Self-Assessment',
   'Online self-serve organisational innovation maturity assessment',
   '$2,500'],
  ['Full Organizational Innovation Assessment (Full OIA)',
   'Expert-led audit. Produces a Company Certificate at Level 1, 2, 3, or 4. Certification fee on outcome: L1 $2,500 / L2 $5,000 / L3 $7,500 / L4 $10,000',
   '$40,000 audit']
];
const pt_software = [
  ['AKAIO – AI-Powered Innovation Platform',     'Ecosystem platform with trend intelligence and partner matching',  'Contact'],
  ['Eureka – Online Subscription',               'Idea management and innovation portfolio software',                '$500 / year'],
  ['Service Innovation Tool',                    'Tool for diagnosing service innovation gaps',                       'TBD'],
  ['QuickGrowth',                                'Software-enabled strategic planning platform for SMEs',             '$5,000']
];
const pt_programs = [
  ['Innovation Academy',                      'Custom learning hub built inside the organisation',       '$50,000'],
  ['GIMI Innovation Coaching',                'Per session $700 / per month $2,000 / per year $12,000',  'Tiered'],
  ['GIMI Innovation Awards – Organization',   'Annual application across 10 award categories',           '$350–$600'],
  ['Innovation Keynote Speech',               '1–2 hour keynote, online or in-person',                   '$25,000']
];

// Group 8 — Memberships
const memberships = [
  ['Student Membership',                  'Students',     '$70'],
  ['Professional Membership',             'Professionals','$200'],
  ['Corporate Membership – Gold',         'Companies',    '$10,000'],
  ['Corporate Membership – Silver',       'Companies',    '$7,000'],
  ['Corporate Membership – Platinum',     'Companies',    '$15,000'],
  ['Organizational Membership – Academia','Universities', '$5,000'],
  ['GIMI Think Tank (community access)',  'Open',         'Free']
];

// ===== DOCUMENT =====
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: '000000' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: '000000' },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 22, bold: true, color: '000000' },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [{
      reference: 'bul',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: 'GIMI Store Structure  |  Page ', font: FONT, size: 18, color: '808080' }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: '808080' })
          ]
        })]
      })
    },
    children: [

      // ===== TITLE =====
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({ text: 'GIMI Store – Structure Blueprint', font: FONT, size: 40, bold: true })]
      }),
      new Paragraph({
        spacing: { after: 320 },
        children: [new TextRun({ text: 'Reference document for the public store layout', font: FONT, size: 22, italics: true })]
      }),

      // ===== EXEC SUMMARY =====
      H1('Executive Summary'),
      P('The GIMI store will hold 65 products organised into 8 discipline-based groups. Visitors browse first by group and then by sub-cluster within each group, with masterclass cohorts and train-the-trainer tracks shown as their own labelled clusters.'),

      // ===== FILTERS =====
      H1('Store Filters'),
      H2('Groups'),
      BUL('Innovation Core – the flagship innovation management pathway and its delivery formats.'),
      BUL('Innovation Elective – specialist certifications adjacent to the core path.'),
      BUL('Future Foresight – foresight professional and trainer certifications.'),
      BUL('Leadership Core – leadership-oriented certifications.'),
      BUL('Consulting Core – the management consulting pathway.'),
      BUL('Books & Guides – published books, guides, and reference materials.'),
      BUL('Programs & Tools – assessments, software, organisational programs, and engagements.'),
      BUL('Memberships – annual access tiers for individuals, companies, and academia.'),

      // ===== INNOVATION CORE =====
      new Paragraph({ children: [], pageBreakBefore: true }),
      H1('Group 1 – Innovation Core'),
      P('10 products. Sub-clusters separate the CIP and CCIO certification series from their masterclass cohort versions.'),

      H3('CIP series'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ic_cip),
      H3('CIP-Masterclass'),
      buildTable(tinyCertW, ['Code','Full Name','Fee'], ic_cip_mc),
      H3('CCIO series'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ic_ccio),
      H3('CCIO-Masterclass'),
      buildTable(tinyCertW, ['Code','Full Name','Fee'], ic_ccio_mc),
      H3('GIMI Impact'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ic_impact),
      H3('Train the Trainer'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ic_trainer),

      // ===== INNOVATION ELECTIVE =====
      new Paragraph({ children: [], pageBreakBefore: true }),
      H1('Group 2 – Innovation Elective'),
      P('10 products. Specialist tracks including Design Thinking, ISO, AI, Tech, Longevity, and Audit.'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], elective),

      // ===== FUTURE FORESIGHT =====
      H1('Group 3 – Future Foresight'),
      P('5 products across the professional series and the train-the-trainer track.'),
      H3('Foresight series'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ff_series),
      H3('Train the Trainer'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], ff_trainer),

      // ===== LEADERSHIP CORE =====
      H1('Group 4 – Leadership Core'),
      P('2 products.'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], leadership),

      // ===== CONSULTING CORE =====
      H1('Group 5 – Consulting Core'),
      P('4 products. The full Management Consulting Institute pathway from Analyst to Leader.'),
      buildTable(certW, ['Code','Full Name','Hours','Fee'], consulting),

      // ===== BOOKS & GUIDES =====
      new Paragraph({ children: [], pageBreakBefore: true }),
      H1('Group 6 – Books & Guides'),
      P('13 products. Sub-clusters separate the technical guides from the storytelling and reference titles.'),
      H3('IMBOK'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_imbok),
      H3('Future Foresight Body of Knowledge'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_ffbok),
      H3('ISO Standards'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_iso),
      H3('Innovation Stories'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_stories),
      H3('Practitioner Tools'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_tools),
      H3('Journal'),
      buildTable(bookW, ['Title','Cluster','Fee'], books_journal),

      // ===== PROGRAMS & TOOLS =====
      new Paragraph({ children: [], pageBreakBefore: true }),
      H1('Group 7 – Programs & Tools'),
      P('14 products. Everything that is not a certification or a book: assessments, audits, software, programs, and engagements.'),

      H3('Individual Assessments'),
      buildTable(programW, ['Product','Notes','Fee'], pt_indiv),
      H3('Organizational Assessments'),
      P('The Full OIA audit produces a Company Certificate at Level 1, 2, 3, or 4. The Company Certificate is not a standalone product, it is the formal outcome of the audit; its level-based fee is shown below.'),
      buildTable(programW, ['Product','Notes','Fee'], pt_org),
      H3('Software & Digital Tools'),
      buildTable(programW, ['Product','Notes','Fee'], pt_software),
      H3('Programs & Engagements'),
      buildTable(programW, ['Product','Notes','Fee'], pt_programs),

      // ===== MEMBERSHIPS =====
      new Paragraph({ children: [], pageBreakBefore: true }),
      H1('Group 8 – Memberships'),
      P('7 access tiers across individual, corporate, academic, and open community options.'),
      buildTable(membW, ['Tier','Audience','Fee'], memberships),

      // ===== OPEN ITEMS =====
      H1('Open Items'),
      P('Items that need a decision or a piece of information from GIMI before the store goes live.'),
      buildTable(openW,
        ['Item','What is needed'],
        [
          ['Group naming',
           'These 8 groups match the Excel CRM Category column plus Books & Guides, Programs & Tools, and Memberships. Confirm the two added groups are correctly named.'],
          ['GIMI Innovation Coaching',
           'Listed as one product with three pricing tiers (session $700, month $2,000, year $12,000). Confirm or break into three separate products.'],
          ['Service Innovation Tool, International Journal of Innovation Science',
           'Prices not yet confirmed; will be pulled from the live store at build time unless GIMI shares an updated list.'],
          ['Any products missing from the list',
           'This blueprint covers 65 products consolidated from the Scheme Courses workbook, the V50 product catalogue (March 2026), and the IEL deck. Flag anything else that should appear in the public store.']
        ]
      )
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  const out = 'C:\\Users\\aelha\\Downloads\\GIMI_Store_Blueprint_v10.docx';
  fs.writeFileSync(out, buf);
  console.log('Wrote', out, buf.length, 'bytes');
});
