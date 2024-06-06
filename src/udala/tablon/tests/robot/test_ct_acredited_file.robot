# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s udala.tablon -t test_acredited_file.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src udala.tablon.testing.UDALA_TABLON_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/udala/tablon/tests/robot/test_acredited_file.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a AcreditedFile
  Given a logged-in site administrator
    and an add AcreditedFile form
   When I type 'My AcreditedFile' into the title field
    and I submit the form
   Then a AcreditedFile with the title 'My AcreditedFile' has been created

Scenario: As a site administrator I can view a AcreditedFile
  Given a logged-in site administrator
    and a AcreditedFile 'My AcreditedFile'
   When I go to the AcreditedFile view
   Then I can see the AcreditedFile title 'My AcreditedFile'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add AcreditedFile form
  Go To  ${PLONE_URL}/++add++AcreditedFile

a AcreditedFile 'My AcreditedFile'
  Create content  type=AcreditedFile  id=my-acredited_file  title=My AcreditedFile

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the AcreditedFile view
  Go To  ${PLONE_URL}/my-acredited_file
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a AcreditedFile with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the AcreditedFile title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
