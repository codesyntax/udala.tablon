# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s udala.tablon -t test_documento_tablon.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src udala.tablon.testing.UDALA_TABLON_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/udala/tablon/tests/robot/test_documento_tablon.robot
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

Scenario: As a site administrator I can add a DocumentoTablon
  Given a logged-in site administrator
    and an add DocumentoTablon form
   When I type 'My DocumentoTablon' into the title field
    and I submit the form
   Then a DocumentoTablon with the title 'My DocumentoTablon' has been created

Scenario: As a site administrator I can view a DocumentoTablon
  Given a logged-in site administrator
    and a DocumentoTablon 'My DocumentoTablon'
   When I go to the DocumentoTablon view
   Then I can see the DocumentoTablon title 'My DocumentoTablon'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add DocumentoTablon form
  Go To  ${PLONE_URL}/++add++DocumentoTablon

a DocumentoTablon 'My DocumentoTablon'
  Create content  type=DocumentoTablon  id=my-documento_tablon  title=My DocumentoTablon

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the DocumentoTablon view
  Go To  ${PLONE_URL}/my-documento_tablon
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a DocumentoTablon with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the DocumentoTablon title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
