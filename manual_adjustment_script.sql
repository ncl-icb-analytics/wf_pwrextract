--Script to duplicate a previous month's PWR data for when a provider does not submit or there are issues with their submission.

DECLARE @SourceFYear NVARCHAR(7)      = '2024-25';
DECLARE @SourceFMonth INT             = 2;
DECLARE @DestinationFYear NVARCHAR(7) = '2024-25';
DECLARE @DestinationFMonth INT        = 3;
DECLARE @TargetOrgCode CHAR(3)        = 'RP4';

DELETE FROM [Data_Lab_NCL_Dev].[JakeK].[wf_pwr_wte]
WHERE 
	fyear = @DestinationFYear 
	AND month = @DestinationFMonth
	AND org_code = @TargetOrgCode;

INSERT INTO [Data_Lab_NCL_Dev].[JakeK].[wf_pwr_wte]
SELECT
	@DestinationFYear AS [fyear], 
	[org_code], [occ], [section], [subcode], 
	@DestinationFMonth AS [month], 
	[count], [unit]
FROM [Data_Lab_NCL_Dev].[JakeK].[wf_pwr_wte]
WHERE 
	fyear = @SourceFYear 
	AND month = @SourceFMonth
	AND org_code = @TargetOrgCode;