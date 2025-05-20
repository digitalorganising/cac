enum QualifyingCondition {
    GoodIndustrialRelations @description("If a ballot should be held in the interests of good industrial relations")
    EvidenceMembersOpposed @description("If there is evidence that members of the union are opposed to it conducting collective bargaining")
    MembershipEvidenceDoubts @description("ONLY if present as per 22(4), NOT if the membership level itself is in doubt")
}

class WhetherToBallotDecision {
    decision_date string
    decision_to_ballot bool
    majority_membership bool
    qualifying_conditions QualifyingCondition[]

    @@assert(consistent_qualifying_conditions, {{ this.qualifying_conditions|length|bool == this.majority_membership|bool }})
}

function ExtractWhetherToBallotDecision(decision_document: string) -> WhetherToBallotDecision {
  client DefaultClient
  prompt #"
    Given the CAC whether-to-ballot decision document below,

    <doc>
    {{ decision_document }}
    </doc>

    {{ ctx.output_format }}

    Before you answer, show your reasoning for these points, then answer as above.

    1. Was the panel satisfied that the majority of workers in the bargaining unit were members of the union?
    2. If there will be a ballot AND the answer to 1 is YES: extract a list of the qualifying conditions that WERE met.
    3. If majority_membership is false then qualifying_conditions MUST be an empty list.
  "#
}

test TestName {
  functions [ExtractWhetherToBallotDecision]
  args {
    decision_document #"
      Case Number: TUR1/1057(2018)
    
    23 July 2018
    
    CENTRAL ARBITRATION COMMITTEE
    
    TRADE UNION AND LABOUR RELATIONS (CONSOLIDATION) ACT 1992 SCHEDULE A1 - COLLECTIVE BARGAINING: RECOGNITION DECISION ON WHETHER TO ARRANGE FOR THE HOLDING OF A SECRET BALLOT
    
    The Parties:
    
    UNISON
    
    and
    
    Abbey Healthcare
    
    1. Introduction
    ---------------
    
    1) UNISON (the Union) submitted an application to the CAC dated 21 June 2018 that it should be recognised for collective bargaining purposes by Abbey Healthcare (the Employer) in respect of a bargaining unit comprising “All Abbey Healthcare employees , including home manager, working in the residential care home of Farnworth Care Home, Church St, Bolton BL4 8AG.” The location of the bargaining unit was given as “Farnworth Care Home, Church St, Bolton BL4 8AG.” The application was received by the CAC on 21 June 2018 and the CAC gave both parties notice of receipt of the application on 22 June 2018. The Employer submitted a response to the CAC dated 28 June 2018 which was copied to the Union.
    
    2) In accordance with section 263 of the Trade Union and Labour Relations (Consolidation) Act 1992 (the Act), the CAC Chairman established a Panel to deal with the case. The Panel consisted of Professor Gillian Morris, Panel Chair, and, as Members, Mr David Crowe and Mr Gerry Veart. The Case Manager appointed to support the Panel was Kate Norgate.
    
    3) By a decision dated 17 July 2018 the Panel accepted the Union’s application. In its response to the Union’s application the Employer agreed that the Union’s proposed bargaining unit was an appropriate bargaining unit.
    
    2. Issue for the Panel
    ----------------------
    
    4) Paragraph 22 of Schedule A1 to the Act (the Schedule) provides that if the CAC is satisfied that a majority of the workers constituting the bargaining unit are members of the union, it must issue a declaration of recognition under paragraph 22(2) unless any of the three qualifying conditions specified in paragraph 22(4) applies. Paragraph 22(3) requires the CAC to hold a ballot even where it has found that a majority of workers constituting the bargaining unit are members of the union if any of these qualifying conditions is fulfilled. The three qualifying conditions are:
    
    a. the CAC is satisfied that a ballot should be held in the interests of good industrial relations;
    
    b. the CAC has evidence, which it considers to be credible, from a significant number of the union members within the bargaining unit that they do not want the union (or unions) to conduct collective bargaining on their behalf;
    
    c. membership evidence is produced which leads the CAC to conclude that there are doubts whether a significant number of the union members within the bargaining unit want the union (or unions) to conduct collective bargaining on their behalf.
    
    The Panel decided that in this case it would be appropriate to decide whether it was satisfied that a majority of the workers constituting the bargaining unit were members of the union as a preliminary issue before asking the parties to make submissions on the application of the qualifying conditions.
    
    3. Summary of the Union’s claim to majority membership
    ------------------------------------------------------
    
    5) On 17 July 2018 the Case Manager wrote to the Union to ascertain whether it was claiming majority membership within the bargaining unit and was therefore submitting that it should be granted recognition without a ballot.
    
    6) In an e-mail to the Case Manager dated 17 July 2018 the Union confirmed that it believed that it had majority membership within the bargaining unit and therefore should be awarded recognition without a ballot. The Union stated that it now had 51 full members within the bargaining unit and that this figure continued to rise. The Union said that it would be happy to provide further evidence of its increasing membership numbers should this be required. The Union said that it was calculating the majority based on the 101 employees which it believed comprised the agreed bargaining unit.
    
    4. Summary of the Employer’s response to the Union’s claim
    ----------------------------------------------------------
    
    7) In a letter to the Employer dated 18 July 2018 the Case Manager invited the Employer to comment on the Union’s claim to majority membership.
    
    8) In an e-mail to the Case Manager dated 20 July 2018 the Employer stated that it had 113 people in the bargaining unit and that the 51 members claimed by the Union did not, therefore, constitute a majority. The Employer stated that it had taken the figure of 113 directly from its payroll report which was maintained daily and was entirely up-to-date. The Employer stated that it believed that the Union had taken its information from an historic Company report and the figure the Union was relying on was out-of-date. The Employer offered to supply evidence of the number of workers in the bargaining unit on a confidential basis if the Panel so required. The Employer said that it disputed the claim that the Union had rising membership, its understanding from staff feedback being that there were members who were cancelling their membership following the tactics and harassment they had felt under from the Union and its representatives.
    
    5. Considerations
    -----------------
    
    9) Paragraph 22 of the Schedule requires the Panel to consider whether it is satisfied that the majority of the workers constituting the bargaining unit are members of the Union. If the Panel is satisfied that a majority of the workers constituting the bargaining unit are members of the Union, it must declare the Union recognised as entitled to conduct collective bargaining on behalf of the workers constituting the bargaining unit unless it decides that any of the three qualifying conditions set out in paragraph 22(4) is fulfilled. If the Panel considers that any of them is fulfilled it must give notice to the parties that it intends to arrange for the holding of a secret ballot.
    
    10) The Union has stated that it has 51 members and that this constitutes a majority based on the 101 employees which it believes comprise the agreed bargaining unit. The Employer has stated that there are 113 workers within the bargaining unit. The Panel notes that the Employer attached to its response to the Union’s application dated 28 June 2018 a spreadsheet listing employee ID numbers and roles and supplied information to the Case Manager on 4 July 2018 for the purposes of a membership and support check listing 115 workers in the bargaining unit. The Panel has received no evidence which leads it to suspect that either party did not act honestly and in good faith in giving information for the purposes of the membership and support check or did not act honestly and in good faith in submitting evidence for this purposes of this decision. The Panel is not, therefore, satisfied that a majority of the workers constituting the bargaining unit are members of the Union.
    
    11) The Panel notes that the Employer has disputed the Union’s claim of rising membership on the basis of its understanding that there are members who are cancelling their membership following the tactics and harassment felt from the Union and its representatives. The Panel makes no findings relating to these allegations and they have played no part in its decision.
    
    6. Decision
    -----------
    
    12) The Panel is not satisfied that a majority of the workers constituting the bargaining unit are members of the Union. The CAC hereby gives notice, pursuant to paragraph 23(2) of the Schedule, that it intends to arrange for the holding of a secret ballot in which the workers constituting the bargaining unit will be asked whether they want the Union to conduct collective bargaining on their behalf.
    
    Panel
    
    Professor Gillian Morris, Panel Chair
    
    Mr David Crowe
    
    Mr Gerry Veart
    
    23 July 2018

    "#
  }
}
