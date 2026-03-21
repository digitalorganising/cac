class IdentifiedCompany {
    type "identified"
    company_number string
}

enum OtherEntityType {
    LocalAuthority
    GovernmentDepartment
    ArmsLengthBody
    University
    IndependentSchool
    Charity
    Other
    Unknown
}

class UnidentifiedCompany {
    type "unidentified"
    subtype OtherEntityType
    sic_codes string[] @description("Should be empty if you have no information about the entity")
}

class GuessedSicCodes {
    type "unidentified"
    subtype "Unknown"
    sic_codes string[]
    reason string @description("The brief reason why you have guessed the SIC codes")
}

class RequiresNewSearch {
    type "requires-new-search"
    suggested_name string @description("Must be different to the original name; use your knowledge of what the company might be registered as")
    reason string @description("The brief reason why a new search is required")
}

function DisambiguateCompany(candidates: string, name: string, unions: string[], application_date: string, bargaining_unit: string, locations: string[]?) -> IdentifiedCompany  | UnidentifiedCompany | RequiresNewSearch {
    client BestClient
    prompt #"
        You are a UK labour researcher working on identifying organisations involved in union recognition decisions. 

        Your job is to disambiguate a company by its name in a recognition decision from a list of candidates provided by Companies House based on its name.
        Alternatively, you may be able to establish that it is some entity that is not a registered company. In this case, you will use your knowledge to provide a suitable SIC code.
        
        To make a decision, you should consider the following as well as a name match or approximate match:
        - The relevance of the specific unions involved (ie whether the industries inferred from the SIC codes match)
        - The relevance of any creation/cessation dates compared to the application date and the previous names of the company if present.
        - The job titles in the bargaining unit (if given) and whether these match the industry of the company.
        - The locations of the bargaining unit, although bear in mind that these might not match the registered
          address and could even be the location of a different company, for example when the bargaining unit is formed of contractors working onsite.
        - Any other knowledge that you already hold about the company.

        If you know that the company is primarily not UK-based, it is still appropriate to use a UK subsidiary if this has relevant classifications etc.
        Do not use or consider company or charity numbers in any of your reasoning - you cannot reliably remember these.

        Name: {{ name }}
        Unions: {{ unions }}
        Application Date: {{ application_date }}
        Bargaining Unit: {{ bargaining_unit }}
        Locations: {{ locations }}

        <candidates>
        {{ candidates }}
        </candidates>

        You must NOT give an identified answer with a company that is not in the list of candidates.
        However, if you believe that a new search of Companies House with a different search term would show the correct company, you should suggest this.
        

        {{ ctx.output_format }}
    "#
}

function GuessSicCodes(name: string, unions: string[], bargaining_unit: string, locations: string[]?) -> GuessedSicCodes {
    client BestClient

    prompt #"
        You are a UK labour researcher and you have encountered a company in a statutory recognition decision which you cannot
        find in the Companies House database, and nor can you identify it as some other entity type like a charity or a government body.

        Use your knowledge to suggest the SIC codes which might apply to this company. If you have no idea what it is, return an empty array.

        Name: {{ name }}
        Unions: {{ unions }}
        Bargaining Unit: {{ bargaining_unit }}
        Locations: {{ locations }}

        {{ ctx.output_format }}
    "#
}


test SimpleDisambiguationTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "date_of_creation": "2021-07-29",
                "company_type": "ltd",
                "company_number": "13537233",
                "title": "MORECO GROUP LIMITED",
                "address_snippet": "Second Floor Park View, Riverside Way, Camberley, United Kingdom, GU15 3YL",
                "description": "13537233 - Incorporated on 29 July 2021",
                "sic_codes": ["47910"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2025-10-30",
                "company_type": "ltd",
                "company_number": "16820199",
                "title": "MORECO GROUP HOLDCO LIMITED",
                "address_snippet": "128 City Road, London, United Kingdom, EC1V 2NX",
                "description": "16820199 - Incorporated on 30 October 2025",
                "sic_codes": ["68100", "68209"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2011-05-11",
                "company_type": "ltd",
                "company_number": "07630017",
                "title": "MORECO LTD",
                "address_snippet": "Unit 4 Central Business Park, Southcote Road, Bournemouth, BH1 3SJ",
                "description": "07630017 - Incorporated on 11 May 2011",
                "sic_codes": ["43999"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2013-10-10",
                "company_type": "ltd",
                "company_number": "08727879",
                "title": "MORECOCK INVESTMENTS LIMITED",
                "address_snippet": "Enterprise House Maris Lane, Trumpington, Cambridge, England, CB2 9LE",
                "description": "08727879 - Incorporated on 10 October 2013",
                "sic_codes": ["68100"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2025-01-30",
                "company_type": "ltd",
                "company_number": "16218548",
                "title": "MORECO CONSTRUCTION LTD",
                "address_snippet": "128 City Road, London, United Kingdom, EC1V 2NX",
                "description": "16218548 - Incorporated on 30 January 2025",
                "sic_codes": ["68100", "68209"],
                "date_of_cessation": null,
                "previous_company_names": null
            }
        ]
        "#
        name "Moreco Group Ltd"
        unions ["Unite the Union"]
        application_date "2025-11-27"
        bargaining_unit #"
            All Moreco Group Ltd employees working at or from the Milk and More Watford Depot
            save for those employed at Assistant Manager Level or above
        "#
        locations ["Milk and More Watford Depot (1 Odhams Trading Estate, Watford WD24 7RY)"]
    }

    @@assert({{ this.company_number == "13537233" }})
}

test ComplexDisambiguationTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "date_of_creation": "1988-02-26",
                "company_type": "ltd",
                "company_number": "02224829",
                "title": "D. BRICE & CO. LIMITED",
                "address_snippet": "Unit 15 57a Croydon Road, Croydon, Surrey, CR0 4WQ",
                "description": "02224829 - Incorporated on 26 February 1988",
                "sic_codes": ["81210"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2011-07-19",
                "company_type": "ltd",
                "company_number": "07710241",
                "title": "DEREK J BRICE BUILDING & LANDSCAPING LIMITED",
                "address_snippet": "Jersey Cottage Mere Green, Hanbury, Droitwich, Worcestershire, United Kingdom, WR9 7DZ",
                "description": "07710241 - Incorporated on 19 July 2011",
                "sic_codes": ["81300"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2023-05-29",
                "company_type": "ltd",
                "company_number": "14899170",
                "title": "BRICE PLUMBING & DRAINAGE LTD",
                "address_snippet": "83 Brow Crescent, Orpington, Kent, United Kingdom, BR5 4LN",
                "description": "14899170 - Dissolved on 29 October 2024",
                "sic_codes": ["43290"],
                "date_of_cessation": "2024-10-29",
                "previous_company_names": null
            },
            {
                "date_of_creation": "2003-05-13",
                "company_type": "ltd",
                "company_number": "04763177",
                "title": "M A BRICE & SON MOLING SERVICES LIMITED",
                "address_snippet": "Nether Court, Abbey Farm, Faversham, Kent, ME13 7BL",
                "description": "04763177 - Incorporated on 13 May 2003",
                "sic_codes": ["43999"],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2002-09-30",
                "company_type": "ltd",
                "company_number": "04548370",
                "title": "LES BRICE HEATING & PLUMBING SERVICES LIMITED",
                "address_snippet": "19 Warren Park Way, Enderby, Leicester, LE19 4SA",
                "description": "04548370 - Dissolved on 28 September 2021",
                "sic_codes": ["43220"],
                "date_of_cessation": "2021-09-28",
                "previous_company_names": null
            }
        ]
        "#
        name "D Brice & Company Ltd- T/as D B Services"
        unions ["United Voices of the World"]
        application_date "2024-07-15"
        bargaining_unit #"
            the cleaners employed by DB Services at James Allen’s Girls’ School
        "#
        locations ["James Allen’s Girls’ School 144 East Dulwich Grove, London, SE22 8TE"]
    }

    @@assert({{ this.company_number == "02224829" }})
}

test OverseasCompanyTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "date_of_creation": "1993-01-01",
                "company_type": "oversea-company",
                "company_number": "FC011471",
                "title": "AMERICAN AIRLINES INC",
                "address_snippet": "1 Skyview Drive, Fort Worth, 76156, United States",
                "description": "FC011471 - First UK establishment opened on 1 January 1993",
                "sic_codes": null,
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "1993-01-01",
                "company_type": "uk-establishment",
                "company_number": "BR002223",
                "title": "AMERICAN AIRLINES, INC.",
                "address_snippet": "Waterside Haa3 West Drayton, Harmondsworth, UB7 0GB",
                "description": "BR002223 - Opened on 1 January 1993",
                "sic_codes": null,
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2023-01-28",
                "company_type": "registered-overseas-entity",
                "company_number": "OE019258",
                "title": "AMERICAN AIRLINES, INC.",
                "address_snippet": "Corporation Service Company 251 Little Falls Drive, Wilmington, New Castle, De, United States, 19808",
                "description": "OE019258 - Registered on 28 January 2023",
                "sic_codes": null,
                "date_of_cessation": null,
                "previous_company_names": null
            },
            ,
            {
                "date_of_creation": "2023-01-28",
                "company_type": "registered-overseas-entity",
                "company_number": "OE019258",
                "title": "AMERICAN AIRLINES, INC.",
                "address_snippet": "Corporation Service Company 251 Little Falls Drive, Wilmington, New Castle, De, United States, 19808",
                "description": "OE019258 - Registered on 28 January 2023",
                "sic_codes": null,
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "1997-04-11",
                "company_type": "ltd",
                "company_number": "03351054",
                "title": "A.A.H. (1997) LIMITED",
                "address_snippet": "The Thomas Cook Business Park, Coningsby Road, Peterborough, Cambs, PE3 8SB",
                "description": "03351054 - Dissolved on 18 May 2014",
                "sic_codes": ["74990"],
                "date_of_cessation": "2014-05-18",
                "previous_company_names": [
                    {
                        "ceased_on": "1997-08-04",
                        "effective_from": "1997-06-03",
                        "name": "AMERICAN AIRLINES HOLIDAYS (1997) LIMITED"
                    },
                    {
                        "ceased_on": "1997-06-03",
                        "effective_from": "1997-04-11",
                        "name": "BEGINGLORY LIMITED"
                    }
                ]
            },
            {
                "date_of_creation": "2008-03-19",
                "company_type": "oversea-company",
                "company_number": "FC028270",
                "title": "AEGEAN AIRLINES SA",
                "address_snippet": "31 Viltanioti Street, 145 64 Kifissia, Athens, Greece",
                "description": "FC028270 - First UK establishment opened on 19 March 2008",
                "sic_codes": null,
                "date_of_cessation": null,
                "previous_company_names": null
            }
        ]
        "#
        name "American Airlines"
        unions ["Unite the Union"]
        application_date "29 March 2016"
        bargaining_unit "All Aircraft Maintenance Technicians"
        locations  ["Heathrow Airport", "London Heathrow Airport"]
    }

    @@assert({{ this.company_number == "FC011471" }})
}

test NewSearchTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "date_of_creation": "1991-08-28",
                "company_type": "ltd",
                "company_number": "02640971",
                "title": "XPO LOGISTICS LIMITED",
                "address_snippet": "Distribution House Eldon Way, Crick, Northampton, Northamptonshire, England, NN6 7SL",
                "description": "02640971 - Incorporated on 28 August 1991",
                "sic_codes": [
                "99999"
                ],
                "date_of_cessation": null,
                "previous_company_names": [
                {
                    "ceased_on": "2024-06-22",
                    "effective_from": "2015-12-01",
                    "name": "LAMBDA 6 LIMITED"
                },
                {
                    "ceased_on": "2015-12-01",
                    "effective_from": "2013-12-30",
                    "name": "NORBERT DENTRESSANGLE SERVICES LIMITED"
                },
                {
                    "ceased_on": "2013-12-30",
                    "effective_from": "1999-12-30",
                    "name": "NORBERT DENTRESSANGLE U.K. LIMITED"
                },
                {
                    "ceased_on": "1999-12-30",
                    "effective_from": "1991-11-15",
                    "name": "ASTON CLINTON HAULAGE COMPANY LIMITED"
                },
                {
                    "ceased_on": "1991-11-15",
                    "effective_from": "1991-08-28",
                    "name": "INCOMEISSUE LIMITED"
                }
                ]
            },
            {
                "date_of_creation": "2024-04-13",
                "company_type": "ltd",
                "company_number": "15642078",
                "title": "VRN LOGISTICS LIMITED",
                "address_snippet": "16 Scrutton Close, London, England, SW12 0AW",
                "description": "15642078 - Dissolved on 16 September 2025",
                "sic_codes": [
                "49410"
                ],
                "date_of_cessation": "2025-09-16",
                "previous_company_names": [
                {
                    "ceased_on": "2024-06-06",
                    "effective_from": "2024-04-13",
                    "name": "XPO LOGISTICS LIMITED"
                }
                ]
            },
            {
                "date_of_creation": "2018-03-26",
                "company_type": "ltd",
                "company_number": "11274161",
                "title": "XP LOGISTICS LTD",
                "address_snippet": "23 Roker Park Avenue, Ickenham, Uxbridge, England, UB10 8ED",
                "description": "11274161 - Incorporated on 26 March 2018",
                "sic_codes": [
                "49410"
                ],
                "date_of_cessation": null,
                "previous_company_names": [
                {
                    "ceased_on": "2023-09-12",
                    "effective_from": "2023-09-07",
                    "name": "XPO LOGISTICS LTD"
                },
                {
                    "ceased_on": "2023-09-07",
                    "effective_from": "2018-03-26",
                    "name": "AMALIA & DARIUS TRANS LTD"
                }
                ]
            },
            {
                "date_of_creation": "2022-07-11",
                "company_type": "ltd",
                "company_number": "14225814",
                "title": "14225814 LTD",
                "address_snippet": "Flat 2, 340-346 Radford Road, Nottingham, Nottinghamshire, United Kingdom, NG7 5GQ",
                "description": "14225814 - Dissolved on 24 December 2024",
                "sic_codes": [
                "74909"
                ],
                "date_of_cessation": "2024-12-24",
                "previous_company_names": [
                {
                    "ceased_on": "2023-03-14",
                    "effective_from": "2022-07-11",
                    "name": "XPO LOGISTICS LIMITED"
                }
                ]
            },
            {
                "date_of_creation": "2013-05-15",
                "company_type": "ltd",
                "company_number": "08530618",
                "title": "XPO LOGISTICS TRUSTEES LIMITED",
                "address_snippet": "Distribution House Eldon Way, Crick, Northampton, Northamptonshire, England, NN6 7SL",
                "description": "08530618 - Incorporated on 15 May 2013",
                "sic_codes": [
                "82990"
                ],
                "date_of_cessation": null,
                "previous_company_names": [
                {
                    "ceased_on": "2022-02-24",
                    "effective_from": "2018-04-05",
                    "name": "XPO LOGISTICS LIMITED"
                },
                {
                    "ceased_on": "2018-04-05",
                    "effective_from": "2017-03-21",
                    "name": "LAMBDA 7 LIMITED"
                },
                {
                    "ceased_on": "2017-03-21",
                    "effective_from": "2015-12-01",
                    "name": "XPO (CIF TRUSTEE) UK LIMITED"
                },
                {
                    "ceased_on": "2015-12-01",
                    "effective_from": "2013-05-15",
                    "name": "NORBERT DENTRESSANGLE CIF TRUSTEE LIMITED"
                }
                ]
            }
        ]
        "#
        name "XPO Logistics"
        unions ["Unite the Union"]
        application_date "18 April 2017"
        bargaining_unit "Drivers"
        locations ["Needham Road, Stowmarket, Suffolk"]
    }

    @@assert({{ this.type == "requires-new-search" }})
    @@assert({{ this.suggested_name == "XPO Transport Solutions UK Limited" }})
}

test LocalAuthorityTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "date_of_creation": "1994-04-11",
                "company_type": "private-limited-guarant-nsc-limited-exemption",
                "company_number": "02917631",
                "title": "THE WEST SUSSEX COUNTY FEDERATION OF WOMEN'S INSTITUTES",
                "address_snippet": "60 Queen Street, Horsham, England, RH13 5AD",
                "description": "02917631 - Incorporated on 11 April 1994",
                "sic_codes": [
                "94990"
                ],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "company_type": "industrial-and-provident-society",
                "company_number": "IP13577R",
                "title": "WEST SUSSEX COUNTY FEDERATION OF WOMEN'S INSTITUTES HOUSE LIMITED",
                "description": "IP13577R - Converted/Closed",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            },
            {
                "date_of_creation": "2010-09-09",
                "company_type": "private-limited-guarant-nsc-limited-exemption",
                "company_number": "07371252",
                "title": "WEST SUSSEX COUNCIL FOR VOLUNTARY YOUTH SERVICES",
                "address_snippet": "Comewell House, North Street, Horsham, West Sussex, England, RH12 1RD",
                "description": "07371252 - Dissolved on 24 February 2015",
                "sic_codes": [
                "94990"
                ],
                "date_of_cessation": "2015-02-24",
                "previous_company_names": null
            },
            {
                "date_of_creation": "1994-02-25",
                "company_type": "private-limited-guarant-nsc-limited-exemption",
                "company_number": "02902472",
                "title": "COUNCIL FOR VOLUNTARY SERVICE NORTHAMPTON AND COUNTY",
                "address_snippet": "Alma Park Woodway Lane, Claybrooke Parva, Lutterworth, Leicestershire, LE17 5FB",
                "description": "02902472 - Incorporated on 25 February 1994 - Liquidation",
                "sic_codes": [
                "94990"
                ],
                "date_of_cessation": null,
                "previous_company_names": null
            },
            {
                "company_type": "industrial-and-provident-society",
                "company_number": "IP12589R",
                "title": "GLAMORGAN COUNTY ALLOTMENTS COUNCIL LIMITED",
                "description": "IP12589R - Converted/Closed",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            }
        ]
        "#
        name "West Sussex County Council"
        unions ["UNISON"]
        application_date "30 September 2020"
        bargaining_unit "the following pay groups within West Sussex County Council: HAY; SMG4; and Public Health/Agenda for Change (AfC)"
        locations ["Chichester", "Horsham", "Worthing", "Bognor", "Crawley"]
    }

    @@assert({{ this.type == "unidentified" }})
    @@assert({{ this.subtype == "LocalAuthority" }})
    @@assert({{ this.sic_codes == ["84110"] }})
}

test CharityTest {
    functions [DisambiguateCompany]
    args {
        candidates #"
        [
            {
                "company_type": "charitable-incorporated-organisation",
                "company_number": "CE042886",
                "title": "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS BATH AND NORTH SOMERSET BRANCH CIO",
                "address_snippet": "",
                "description": "CE042886 - Registered externally as 1217092",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            },
            {
                "company_type": "charitable-incorporated-organisation",
                "company_number": "CE042100",
                "title": "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS BEDFORDSHIRE SOUTH  AND MID HERTFORDSHIRE BRANCH CIO",
                "address_snippet": "",
                "description": "CE042100 - Registered externally as 1216043",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            },
            {
                "company_type": "charitable-incorporated-organisation",
                "company_number": "CE042874",
                "title": "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS BLACKPOOL AND NORTH LANCASHIRE BRANCH CIO",
                "address_snippet": "",
                "description": "CE042874 - Registered externally as 1217076",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            },
            {
                "company_type": "charitable-incorporated-organisation",
                "company_number": "CE037014",
                "title": "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS - BOLTON AND DISTRICT BRANCH CIO",
                "description": "CE037014 - Registered externally as 1209361",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            },
            {
                "company_type": "charitable-incorporated-organisation",
                "company_number": "CE040771",
                "title": "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS BOURNEMOUTH, NEW FOREST AND DISTRICT BRANCH CIO",
                "description": "CE040771 - Registered externally as 1214300",
                "sic_codes": null,
                "date_of_cessation": null,
                "date_of_creation": null,
                "previous_company_names": null
            }
        ]
        "#
        name "RSA (The Royal Society for the Encouragement of the Arts, Manufactures and Commerce)"
        unions ["IWGB"]
        application_date "30 June 2022"
        bargaining_unit "all staff members of the RSA (including permanent, temporary and fixed-term staff and paid interns), apart from the Senior Management Team (consisting at time of writing of the Chief Executive, Chief Operating Officer, incoming Chief Impact Officer and the eight directors)"
        locations ["The Royal Society for the Encouragement of the Arts, Manufacturers and Commerce, 8 John Adam Street London, WC2N 6EZ"]
    }

    @@assert({{ this.type == "unidentified" }})
    @@assert({{ this.subtype == "Charity" }})
    @@assert({{ this.sic_codes == ["94120", "72200", "94990"] }})
}

test GuessSicCodesTest {
    functions [GuessSicCodes]
    args {
        name "Emirates"
        unions ["Unite the Union"]
        bargaining_unit "Operational services staff employed at Gatwick Airport specifically including Duty Officers, Supervisors, Ticket Desk Agents, Senior Airport Agents, Airport Agents and specifically excluding Airport Services Manager"
        locations ["Gatwick Airport, Horley, Gatwick RH6 0NP"]
    }

    @@assert({{ this.sic_codes == ["51101", "52230"] }})
}