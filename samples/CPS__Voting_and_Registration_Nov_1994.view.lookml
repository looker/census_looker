- view: CPS__Voting_and_Registration_Nov_1994
  sql_table_name: [ENTER DATA FILE NAME HERE]


  fields:
  - dimension: peeduca
    sql: ${TABLE}.PEEDUCA
    label: "Highest level of school completed"
    view_label: 'Demographic Variables'
    type: string
    sql_case:
      Not in Universe: |
        ${TABLE}.peeduca = -1
      Less Than 1st Grade: |
        ${TABLE}.peeduca = 31
      1st,2nd,3rd Or 4th Grade: |
        ${TABLE}.peeduca = 32
      5th Or 6th Grade: |
        ${TABLE}.peeduca = 33
      7th Or 8th Grade: |
        ${TABLE}.peeduca = 34
      9th Grade: |
        ${TABLE}.peeduca = 35
      10th Grade: |
        ${TABLE}.peeduca = 36
      11th Grade: |
        ${TABLE}.peeduca = 37
      12th Grade No Diploma: |
        ${TABLE}.peeduca = 38
      High School Grad-Diploma Or Equiv (ged): |
        ${TABLE}.peeduca = 39
      Some College But No Degree: |
        ${TABLE}.peeduca = 40
      Associate Degree-Occupational/Vocationl: |
        ${TABLE}.peeduca = 41
      Associate Deg.-Academic Program: |
        ${TABLE}.peeduca = 42
      Bachelor's Degree(ex":"ba,ab,bs): |
        ${TABLE}.peeduca = 43
      MASTER'S DEGREE(EX":"MA,MS,MEng,MEd,MSW): |
        ${TABLE}.peeduca = 44
      Professional School Deg(ex":"md,dds,dvm): |
        ${TABLE}.peeduca = 45
      DOCTORATE DEGREE(EX":"PhD,EdD): |
        ${TABLE}.peeduca = 46


  - dimension: pemaritl
    sql: ${TABLE}.PEMARITL
    label: "Marital status"
    view_label: 'Demographic Variables'
    type: string
    sql_case:
      Not in Universe: |
        ${TABLE}.pemaritl = -1
      Married - Spouse Present: |
        ${TABLE}.pemaritl = 1
      Married-Spouse Absent: |
        ${TABLE}.pemaritl = 2
      Widowed: |
        ${TABLE}.pemaritl = 3
      Divorced: |
        ${TABLE}.pemaritl = 4
      Separated: |
        ${TABLE}.pemaritl = 5
      Never Married: |
        ${TABLE}.pemaritl = 6


  - dimension: pesex
    sql: ${TABLE}.PESEX
    label: "Sex"
    view_label: 'Demographic Variables'
    type: string
    sql_case:
      Male: |
        ${TABLE}.pesex = 1
      Female: |
        ${TABLE}.pesex = 2


  - dimension: prtage
    label: " age topcoded at 85, 90 or 80 (see full description)"
    view_label: 'Demographic Variables'
    type: tier
    tiers: [0,23,45,68,90]
    style: classic
    sql: ${TABLE}.PRTAGE
    sql: CASE WHEN ${TABLE}.prtage between 0 AND 90 THEN ${TABLE}.prtage END

  - dimension: prtfage
    sql: ${TABLE}.PRTFAGE
    label: "Top coded flag for age"
    view_label: 'Demographic Variables'
    type: string
    sql_case:
      No Top Code: |
        ${TABLE}.prtfage = 0
      Top Coded Value For Age: |
        ${TABLE}.prtfage = 1


  - dimension: perace
    sql: ${TABLE}.PERACE
    label: "Race of respondent"
    view_label: 'Demographic Variables'
    type: string
    sql_case:
      White: |
        ${TABLE}.perace = 1
      Black: |
        ${TABLE}.perace = 2
      American Indian, Aleut, Eskimo: |
        ${TABLE}.perace = 3
      Asian or Pacific Islander: |
        ${TABLE}.perace = 4
      Other: |
        ${TABLE}.perace = 5


  - dimension: gtcmsa
    sql: ${TABLE}.GTCMSA
    label: "Consolidated msa code"
    view_label: 'Geography Variables'
    type: string
    sql_case:
      Not Identified or NonMetropolitan: |
        ${TABLE}.gtcmsa = 0
      Boston-Worcester-Lawrence, MA-NH-ME-CT: |
        ${TABLE}.gtcmsa = 7
      Chicago-Gary-Kenosha, IL-IN-WI: |
        ${TABLE}.gtcmsa = 14
      Cincinnati-Hamilton, OH-KY-IN: |
        ${TABLE}.gtcmsa = 21
      Cleveland-Akron, OH: |
        ${TABLE}.gtcmsa = 28
      Dallas-Fort Worth, TX: |
        ${TABLE}.gtcmsa = 31
      Denver-Boulder-Greeley, CO: |
        ${TABLE}.gtcmsa = 34
      Detroit-Ann Arbor-Flint, MI: |
        ${TABLE}.gtcmsa = 35
      Houston-Galveston-Brazoria, TX: |
        ${TABLE}.gtcmsa = 42
      Los Angeles-Riverside-Orange County, CA: |
        ${TABLE}.gtcmsa = 49
      Miami-Fort Lauderdale, FL: |
        ${TABLE}.gtcmsa = 56
      Milwaukee-Racine, WI: |
        ${TABLE}.gtcmsa = 63
      New York-Northern New Jersey-Long Island, NY-NJ-CT-PA: |
        ${TABLE}.gtcmsa = 70
      Philadelphia-Wilmington-Atlantic City, PA-NJ-DE-MD: |
        ${TABLE}.gtcmsa = 77
      Portland-Salem, OR-WA: |
        ${TABLE}.gtcmsa = 79
      Sacramento-Yolo, CA: |
        ${TABLE}.gtcmsa = 82
      San Francisco-Oakland-San Jose, CA: |
        ${TABLE}.gtcmsa = 84
      Seattle-Tacoma-Bremerton, WA: |
        ${TABLE}.gtcmsa = 91
      Washington-Baltimore, DC-MD-VA-WV: |
        ${TABLE}.gtcmsa = 97


  - dimension: gestcen
    sql: ${TABLE}.GESTCEN
    label: "Census state code"
    view_label: 'Geography Variables'
    type: string
    sql_case:
      ME: |
        ${TABLE}.gestcen = 11
      NH: |
        ${TABLE}.gestcen = 12
      VT: |
        ${TABLE}.gestcen = 13
      MA: |
        ${TABLE}.gestcen = 14
      RI: |
        ${TABLE}.gestcen = 15
      CT: |
        ${TABLE}.gestcen = 16
      NY: |
        ${TABLE}.gestcen = 21
      NJ: |
        ${TABLE}.gestcen = 22
      PA: |
        ${TABLE}.gestcen = 23
      OH: |
        ${TABLE}.gestcen = 31
      IN: |
        ${TABLE}.gestcen = 32
      IL: |
        ${TABLE}.gestcen = 33
      MI: |
        ${TABLE}.gestcen = 34
      WI: |
        ${TABLE}.gestcen = 35
      MN: |
        ${TABLE}.gestcen = 41
      IA: |
        ${TABLE}.gestcen = 42
      MO: |
        ${TABLE}.gestcen = 43
      ND: |
        ${TABLE}.gestcen = 44
      SD: |
        ${TABLE}.gestcen = 45
      NE: |
        ${TABLE}.gestcen = 46
      KS: |
        ${TABLE}.gestcen = 47
      DE: |
        ${TABLE}.gestcen = 51
      MD: |
        ${TABLE}.gestcen = 52
      DC: |
        ${TABLE}.gestcen = 53
      VA: |
        ${TABLE}.gestcen = 54
      WV: |
        ${TABLE}.gestcen = 55
      NC: |
        ${TABLE}.gestcen = 56
      SC: |
        ${TABLE}.gestcen = 57
      GA: |
        ${TABLE}.gestcen = 58
      FL: |
        ${TABLE}.gestcen = 59
      KY: |
        ${TABLE}.gestcen = 61
      TN: |
        ${TABLE}.gestcen = 62
      AL: |
        ${TABLE}.gestcen = 63
      MS: |
        ${TABLE}.gestcen = 64
      AR: |
        ${TABLE}.gestcen = 71
      LA: |
        ${TABLE}.gestcen = 72
      OK: |
        ${TABLE}.gestcen = 73
      TX: |
        ${TABLE}.gestcen = 74
      MT: |
        ${TABLE}.gestcen = 81
      ID: |
        ${TABLE}.gestcen = 82
      WY: |
        ${TABLE}.gestcen = 83
      CO: |
        ${TABLE}.gestcen = 84
      NM: |
        ${TABLE}.gestcen = 85
      AZ: |
        ${TABLE}.gestcen = 86
      UT: |
        ${TABLE}.gestcen = 87
      NV: |
        ${TABLE}.gestcen = 88
      WA: |
        ${TABLE}.gestcen = 91
      OR: |
        ${TABLE}.gestcen = 92
      CA: |
        ${TABLE}.gestcen = 93
      AK: |
        ${TABLE}.gestcen = 94
      HI: |
        ${TABLE}.gestcen = 95


  - dimension: pternwa
    label: "Weekly earnings,amount-recode"
    view_label: 'Earnings Variables'
    type: tier
    tiers: [0,722,1443,2164,2885]
    style: classic
    sql: ${TABLE}.PTERNWA
    sql: CASE WHEN ${TABLE}.pternwa between 0.0 AND 2884.61 THEN ${TABLE}.pternwa END

  - dimension: prvel
    sql: ${TABLE}.PRVEL
    label: "Voting eligibility recode"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      Eligible for voting and registration questions: |
        ${TABLE}.prvel = 1
      In universe, but no data available: |
        ${TABLE}.prvel = 2
      Not eligible for voting and registration questions: |
        ${TABLE}.prvel = 3


  - dimension: pes3
    sql: ${TABLE}.PES3
    label: "Vote in the november _ election?"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      No response (N/A): |
        ${TABLE}.pes3 = -9
      Refused: |
        ${TABLE}.pes3 = -3
      Don't Know: |
        ${TABLE}.pes3 = -2
      Not in Universe: |
        ${TABLE}.pes3 = -1
      Yes: |
        ${TABLE}.pes3 = 1
      No: |
        ${TABLE}.pes3 = 2


  - dimension: pes4
    sql: ${TABLE}.PES4
    label: "Registered to vote in the november _ election?"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      No response (N/A): |
        ${TABLE}.pes4 = -9
      Refused: |
        ${TABLE}.pes4 = -3
      Don't Know: |
        ${TABLE}.pes4 = -2
      Not in Universe: |
        ${TABLE}.pes4 = -1
      Yes: |
        ${TABLE}.pes4 = 1
      No: |
        ${TABLE}.pes4 = 2


  - dimension: pes5
    sql: ${TABLE}.PES5
    label: "Time of day voted?"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      No response (N/A): |
        ${TABLE}.pes5 = -9
      Refused: |
        ${TABLE}.pes5 = -3
      Don't Know: |
        ${TABLE}.pes5 = -2
      Not in Universe: |
        ${TABLE}.pes5 = -1
      Before noon: |
        ${TABLE}.pes5 = 1
      Noon to 4 p.m.: |
        ${TABLE}.pes5 = 2
      4 p.m. to 6 p.m.: |
        ${TABLE}.pes5 = 3
      After 6 p.m.: |
        ${TABLE}.pes5 = 4
      Voted absentee: |
        ${TABLE}.pes5 = 5


  - dimension: pes6
    sql: ${TABLE}.PES6
    label: "Time at current address"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      No response (N/A): |
        ${TABLE}.pes6 = -9
      Refused: |
        ${TABLE}.pes6 = -3
      Don't Know: |
        ${TABLE}.pes6 = -2
      Not in Universe: |
        ${TABLE}.pes6 = -1
      Less than 1 month: |
        ${TABLE}.pes6 = 1
      1-6 months: |
        ${TABLE}.pes6 = 2
      7-11 months: |
        ${TABLE}.pes6 = 3
      1-2 years: |
        ${TABLE}.pes6 = 4
      3-4 years: |
        ${TABLE}.pes6 = 5
      5 years or longer: |
        ${TABLE}.pes6 = 6


  - dimension: pes7
    sql: ${TABLE}.PES7
    label: "Self or other reported for person"
    view_label: 'Voting and Registration Supplement Variables'
    type: string
    sql_case:
      No response (N/A): |
        ${TABLE}.pes7 = -9
      Self: |
        ${TABLE}.pes7 = 1
      Other: |
        ${TABLE}.pes7 = 2


