# check devices
Feature: Test commands and attributes

Scenario: Check attribute for test device
	Given a device called sys/tg_test/1
	Then the attribute State is RUNNING

Scenario: Call Command and check result
	Given a device called sys/tg_test/1
	When I call the command State()
	Then the result is RUNNING

Scenario: Call Command and test attribute for database
	Given a device called sys/database/2
	When I call the command State()
	Then the result is ON

Scenario: Test DevString command
	Given a device called sys/tg_test/1
	When I call the command DevString(Hello World!)
	Then the result is Hello World!

Scenario: Test short_spectrum_ro type
	Given a device called sys/tg_test/1
	Then the attribute short_spectrum_ro is np.ndarray

Scenario: Test short_spectrum type
	Given a device called sys/tg_test/1
	Then the attribute short_spectrum is np.ndarray