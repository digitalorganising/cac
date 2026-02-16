class IdentifiedCompany {
    type "identified"
    company_number string
    company_type string
    sic_codes string[]
}

class UnidentifiedCompany {
    type "unidentified"
    reason string @description("The reason why the company could not be identified alongside considerations of what the company might have been")
}

function DisambiguateCompany(candidates: string, name: string, unions: string[], application_date: string, bargaining_unit: string, locations: string[]?) -> IdentifiedCompany | UnidentifiedCompany {
    client BestClient
    prompt #"
        You are a UK labour researcher working on identifying companies involved in union recognition decisions. 

        Your job is to disambiguate a company by its name in a recognition decision from a list of candidates provided by Companies House.
        
        To make a decision, you should consider the following as well as a name match or approximate match:
        - The relevance of the specific unions involved (ie whether the industries inferred from the SIC codes match)
        - The relevance of any creation/cessation dates compared to the application date and the previous names of the company if present.
        - The job titles in the bargaining unit (if given) and whether these match the industry of the company.
        - The locations of the bargaining unit, although bear in mind that these might not match the registered
          address and could even be the location of a different company, for example when the bargaining unit is formed of contractors working onsite.
        - Any other knowledge that you already hold about the company.

        You may not be able to identify a company because of ambiguity, or perhaps the company is actually a charity, or some other reason.

        Name: {{ name }}
        Unions: {{ unions }}
        Application Date: {{ application_date }}
        Bargaining Unit: {{ bargaining_unit }}
        Locations: {{ locations }}

        <candidates>
        {{ candidates }}
        </candidates>

        You must NOT answer with a company that is not in the list of candidates.

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
}