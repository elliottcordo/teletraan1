grant exec on [DW_DQ_Infa_Teletran_Watch_Daily]  to appuser
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE proc [dbo].[DW_DQ_Infa_Teletran_Watch_Daily]
  @workflow_name varchar(50)                
as
select top 1 
  workflow_name as name,
  start_time,
  end_time ,
  case 
    when b.run_err_code  <> 0 then 1
    else 0 end as status,
  case 
    when b.run_err_code <> 0 then run_err_msg
    when b.run_status_code = 1 then 'success'
    when b.run_status_code = 6 then 'running'
    else 'unknown' end as status_message
from  infarep..REP_WFLOW_RUN b with (nolock)
where workflow_name = @workflow_name     
         
  and start_time >= cast(convert(varchar(12),getdate(), 101) as datetime) 
order by start_time desc
  
--dbo.DW_DQ_Infa_Teletran_Watch'wf_dw_load_intraday'
--dbo.DW_DQ_Infa_Teletran_Watch'wf_contracts'

--dbo.DW_DQ_Infa_Teletran_Watch'wf_edw_loa
d'

