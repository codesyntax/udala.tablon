# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s udala.tablon -t test_tablon.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src udala.tablon.testing.UDALA_TABLON_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/udala/tablon/tests/robot/test_tablon.robot
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

Scenario: As a site administrator I can add a Tablon
  Given a logged-in site administrator
    and an add Tablon form
   When I type 'My Tablon' into the title field
    and I submit the form
   Then a Tablon with the title 'My Tablon' has been created

Scenario: As a site administrator I can view a Tablon
  Given a logged-in site administrator
    and a Tablon 'My Tablon'
   When I go to the Tablon view
   Then I can see the Tablon title 'My Tablon'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Tablon form
  Go To  ${PLONE_URL}/++add++Tablon

a Tablon 'My Tablon'
  Create content  type=Tablon  id=my-tablon  title=My Tablon

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Tablon view
  Go To  ${PLONE_URL}/my-tablon
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Tablon with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Tablon title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
