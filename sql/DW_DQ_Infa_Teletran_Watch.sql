
alter proc [dbo].[DW_DQ_Infa_Teletran_Watch]
  @workflow_name varchar(50)                
as
select a.workflow_name as name,
  last_start_time,
  last_end_time ,
  case 
    when b.run_err_code  <> 0 then 1
    else 0 end as status,
  case 
    when b.run_err_code <> 0 then run_err_msg
    when b.run_status_code = 1 then 'success'
    when b.run_status_code = 6 then 'running'
    else 'unknown' end as status_message
from (
    select workflow_name,
      max(start_time) as last_start_time, 
      max(end_time) as last_end_time,
      max(workflow_run_id) as workflow_run_id
    from infarep..REP_WFLOW_RUN with (nolock)
    where workflow_name = @workflow_name              
      and start_time >= getdate() -1   
    group by workflow_name) a
  join infarep..REP_WFLOW_RUN b on b.workflow_run_id = a.workflow_run_id


--dbo.DW_DQ_Infa_Teletran_Watch'wf_dw_load_intraday'
--dbo.DW_DQ_Infa_Teletran_Watch'wf_contracts'

--dbo.DW_DQ_Infa_Teletran_Watch'wf_edw_load'


