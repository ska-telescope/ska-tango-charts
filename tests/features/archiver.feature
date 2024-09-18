#check device is ON
@skip
Scenario: Test Configuration Manager device is ON
	Given a device called archiving/hdbpp/confmanager01
	When I call the command state()
	Then the attribute DevState is ON

@skip
Scenario: Test Event Subscriber device is ON
	Given a device called archiving/hdbpp/eventsubscriber01
	When I call the command state()
	Then the attribute DevState is ON

#check archiving is started
@skip
Scenario: Check archiving
	Given a Configuration Manager called archiving/hdbpp/confmanager01 and an Event Subscriber called archiving/hdbpp/eventsubscriber01
	When I request to archive the attribute sys/tg_test/1/double_scalar
	Then after 1000 milliseconds the Archiving is Started
