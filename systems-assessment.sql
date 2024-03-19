SELECT  [responseLineId]
	  ,case when k.questionId=8 THEN 'Availability of DQ SOPs'
		  when k.questionId=9 THEN 'Internal data quality checks'
		  when k.questionId=10 THEN 'Data Quality Audits in the last 6 months'
		  when k.questionId=11 THEN 'DQI Plan'
		  when k.questionId=12 THEN 'Feedback on data quality for planning'
		  when k.questionId=13 THEN 'Regular review of data for decision making'
		  when k.questionId=14 THEN 'MOH HIV Target Awareness'
		  when k.questionId=45 THEN 'Monthly Performance Monitoring'
		  when k.questionId IN(85,103) then 'MOH 362'
	      when k.questionId IN(86,104) then 'MOH 366'
		  when k.questionId IN(87,105) then 'MOH 731'
	      when k.questionId IN(88,106) then 'MOH 729B'
		  when k.questionId IN(89,107) then 'MOH 730B'
		  when k.questionId IN(90,108) then 'MOH 405'
		  when k.questionId IN(91,109) then 'MOH 333'
		  when k.questionId IN(92,110) then 'MOH 406'
		  when k.questionId IN(93,111) then 'MOH 408'
		  when k.questionId=100 then 'Data Upload to NDWH'
	      when k.questionId=25 then 'Backup SOPs'
		  when k.questionId=27 then 'EMR Based DQA'
		  when k.questionId IN(74,75,76,112) then 'Number of staff resposible for data management'
		  when k.questionId IN(77,78,79,113) then 'Staff trained on M&E Tools'
		  when k.questionId IN(97) then 'POC'
	      when k.questionId in(98) then 'Retrospective'
		else q.questionName
	  END AS [question]	
	  ,case when q.questionId in(74,77) then 'HTS'
	        when q.questionId in(75,78) then 'PMTCT'
			when q.questionId in(76,79) then 'C&T'			
			when q.questionId in(112,113) then 'Overall' end as [category]
	  , case when k.questionId IN(74,75,76,112,77,78,79,113) then 'Staff M&E Training'
	        when k.questionId IN(8,9,10,11,12,13,14,45) then 'Data Management Processes'
			when k.questionId IN(94) and oi.optionItemName not in ('No','NA') then 'EMR In Use' 
	        when k.questionId in(96) and oi.optionItemName not in ('No','NA') then 'Current Version'
	   end as [identifier]
	  ,s.sectionName section
	  ,q.questionId
	  , case when k.questionId in(96) and oi.optionItemName ='Yes' then 'Kenya EMR' 
    else (
        case 
            when oi.optionItemName is null then k.value
            else (
                case 
                    when k.questionId IN (85,86,87,88,89,90,91,92,93) then 'Available'
                    when k.questionId IN (103,104,105,106,107,108,109,110,111) then 'In Use'
                    else oi.optionItemName 
                end
            )
        end
    )
end [response]	 
			,1 [value]	
			,k.score
	  ,a.assessmentName [assessment]  
	  ,YEAR(startDate) [year]
	 ,FORMAT(startDate, 'MMMM-yyyy') [month_year]
	  ,ou.orgUnitName facility	  
	  ,county
	  ,sub_county
   
      ,le.orgLevelName level      
     
  FROM [e_dqa].[dbo].[sys_response_lines] k
  inner join [e_dqa].[dbo].[sys_questions] q on k.questionId = q.questionId
  inner join [e_dqa].[dbo].[sys_sections] s on q.sectionId = s.sectionId 
  left join  [e_dqa].[dbo].[sys_option_items] oi on try_parse(k.value as int) = oi.optionItemId
  inner join [e_dqa].[dbo].sys_responses r on r.responseId = k.responseId
  inner join [e_dqa].[dbo].assessments a on a.assessmentId = r.assessmentId
  inner join [e_dqa].[dbo].org_levels le on le.orgLevelId = a.orgLevelId
  join (select orgUnitId,orgUnitName,subCountyId,countyId from org_units where orgLevelId=4) ou on ou.orgUnitId = r.facilityId
  join (select orgUnitId as countyId,   CONCAT(UPPER(SUBSTRING(orgUnitName, 1, 1)),LOWER(SUBSTRING(orgUnitName, 2, LEN(orgUnitName) - 1)))  as county from org_units where [orgLevelId] = 2) as counties on counties.countyId = ou.countyId
  left join (select  orgUnitId as subCountyId, orgUnitName as sub_county from org_units where [orgLevelId] = 3) as subCounties on subCounties.subCountyId = ou.subCountyId
