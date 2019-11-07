from datetime import  timedelta

def write_odm_line( oc_item_name, odk_item_value, is_date=False, is_time=False, is_numeric=False, is_utf8 = False):
    _one_line = ''
    if (odk_item_value):
        _this_value = odk_item_value
        if (is_date):
            _this_value = odk_item_value.strftime('%Y-%m-%d')
        if (is_time):
            # add an extra hour for the time zone
            corrected_time = odk_item_value + timedelta(hours=-1)
            _this_value = corrected_time.strftime('%H:%M')
        if (is_numeric):
            _this_value = str(odk_item_value)
        if (is_utf8):
            # make exception for the &
            _this_value = _this_value.replace('&', '&amp;')
            _this_value = str(_this_value.encode(encoding="ascii",errors="xmlcharrefreplace"))
            # now we have something like b'some text &amp; more' so we want to loose the first two characters and the last one
            # TODO: make this nicer somehow
            _this_value = _this_value[2:]
            _this_value = _this_value[:-1]
                    
        _one_line = _one_line + '            <ItemData ItemOID="' + oc_item_name + '" Value="' + _this_value + '"/>'
    else:
        _one_line = _one_line + '            <ItemData ItemOID="' + oc_item_name + '" Value=""/>'
    #print(_one_line)
    return _one_line

def compose_lamp(study_subject_oid, data_odk):
    _odm_data = ''
    _odm_data = _odm_data + '<ODM>'
    _odm_data = _odm_data + '  <ClinicalData StudyOID="S_MA006_HS">'
    _odm_data = _odm_data + '    <SubjectData SubjectKey="' + study_subject_oid + '">'
    _odm_data = _odm_data + '      <StudyEventData StudyEventOID="SE_BASELINE_9367">'
    _odm_data = _odm_data + '        <FormData FormOID="F_MA006HSRDTMI_3111_12">'
    _odm_data = _odm_data + '          <ItemGroupData ItemGroupOID="IG_MA006_UNGROUPED_6584" ItemGroupRepeatKey="1" TransactionType="Insert">'
    # section a
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_D', data_odk['GENERAL_INFORMATION_LAMP_D'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_INIT', data_odk['GENERAL_INFORMATION_LAMP_INIT'])
    # section b
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_POS_PAN', data_odk['TEST_LAMP_LAMP_POS_PAN'])
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_POS_PF', data_odk['TEST_LAMP_LAMP_POS_PF'])
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_POS_PV', data_odk['TEST_LAMP_LAMP_POS_PV'])
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_T', data_odk['TEST_LAMP_LAMP_T'], is_time=True)
    # section c
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_COMMENTS', data_odk['COMMENT_LAMP_COMMENTS'])

    _odm_data = _odm_data + '          </ItemGroupData>'
    _odm_data = _odm_data + '        </FormData>'
    _odm_data = _odm_data + '      </StudyEventData>'
    _odm_data = _odm_data + '    </SubjectData>'
    _odm_data = _odm_data + '  </ClinicalData>'
    _odm_data = _odm_data + '</ODM>'

    return _odm_data

def compose_misca(study_subject_oid, data_odk):
    _odm_data = ''
    _odm_data = _odm_data + '<ODM>'
    _odm_data = _odm_data + '  <ClinicalData StudyOID="S_MA006_HS">'
    _odm_data = _odm_data + '    <SubjectData SubjectKey="' + study_subject_oid + '">'
    _odm_data = _odm_data + '      <StudyEventData StudyEventOID="SE_BASELINE_9367">'
    _odm_data = _odm_data + '        <FormData FormOID="F_MA006HSRDTMI_9049_16">'
    _odm_data = _odm_data + '          <ItemGroupData ItemGroupOID="IG_MA006_MISCA" ItemGroupRepeatKey="' + str(data_odk['_ORDINAL_NUMBER']) + '" TransactionType="Insert">'
    
    # section a
    _odm_data = _odm_data + write_odm_line('I_MA006_N', data_odk['BABY_DIED_PREG_N'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_P_AGE', data_odk['BABY_DIED_AGE'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_WHEN', data_odk['BABY_DIED_WHEN'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MONTH', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_MONTH'])
    _odm_data = _odm_data + write_odm_line('I_MA006_6_MONTH', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_6_MONTH'])
    _odm_data = _odm_data + write_odm_line('I_MA006_STATE', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_STATE'])
    _odm_data = _odm_data + write_odm_line('I_MA006_P_WEIGHT', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_WEIGHT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_GENDER', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_GENDER'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_ANTENAT', data_odk['BABY_DIED_PREG_BABY_DIED_PREG_ANTENAT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_AFT_PREG_WHEN', data_odk['BABY_DIED_AFT_PREG_BABY_DIED_AFT_PREG_WHEN'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_DELI_WHERE', data_odk['BABY_DIED_AFT_PREG_BABY_DIED_AFT_PREG_DELI_WHERE'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_DELI_WHERE_OT', data_odk['BABY_DIED_AFT_PREG_BABY_DIED_AFT_PREG_DELI_WHERE_OT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_DELI_HOW', data_odk['BABY_DIED_AFT_PREG_BABY_DIED_AFT_PREG_DELI_HOW'], is_numeric=True)

    # closing it all
    _odm_data = _odm_data + '          </ItemGroupData>'
    _odm_data = _odm_data + '        </FormData>'
    _odm_data = _odm_data + '      </StudyEventData>'
    _odm_data = _odm_data + '    </SubjectData>'
    _odm_data = _odm_data + '  </ClinicalData>'
    _odm_data = _odm_data + '</ODM>'

    return _odm_data


def compose_reader(study_subject_oid, data_odk):
    _odm_data = ''
    _odm_data = _odm_data + '<ODM>'
    _odm_data = _odm_data + '  <ClinicalData StudyOID="S_MA006_HS">'
    _odm_data = _odm_data + '    <SubjectData SubjectKey="' + study_subject_oid + '">'
    _odm_data = _odm_data + '      <StudyEventData StudyEventOID="SE_BASELINE_9367">'
    _odm_data = _odm_data + '        <FormData FormOID="F_MA006HSRDTMI_13">'
    _odm_data = _odm_data + '          <ItemGroupData ItemGroupOID="IG_MA006_UNGROUPED" ItemGroupRepeatKey="1" TransactionType="Insert">'
    
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_COMMENTS', data_odk['COMMENT_HS_RDT_COMMENTS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_D', data_odk['GENERAL_INFORMATION_HS_RDT_R1_D'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_FP', data_odk['HS_RDT_TEST_HS_RDT_R1_FP'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_INIT', data_odk['GENERAL_INFORMATION_HS_RDT_R1_INIT'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_POS', data_odk['HS_RDT_TEST_HS_RDT_R1_POS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_SCALE', data_odk['HS_RDT_TEST_HS_RDT_R1_SCALE'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HS_RDT_R1_T', data_odk['HS_RDT_TEST_HS_RDT_R1_T'], is_time=True)
    
    _odm_data = _odm_data + '          </ItemGroupData>'
    _odm_data = _odm_data + '        </FormData>'
    _odm_data = _odm_data + '      </StudyEventData>'
    _odm_data = _odm_data + '    </SubjectData>'
    _odm_data = _odm_data + '  </ClinicalData>'
    _odm_data = _odm_data + '</ODM>'

    return _odm_data

def compose_screening(study_subject_oid, data_odk):
    _odm_data = ''
    _odm_data = _odm_data + '<ODM>'
    _odm_data = _odm_data + '  <ClinicalData StudyOID="S_MA006_HS">'
    _odm_data = _odm_data + '    <SubjectData SubjectKey="' + study_subject_oid + '">'
    _odm_data = _odm_data + '      <StudyEventData StudyEventOID="SE_BASELINE_9367">'
    _odm_data = _odm_data + '        <FormData FormOID="F_MA006HSRDTMI_9049_16">'
    _odm_data = _odm_data + '          <ItemGroupData ItemGroupOID="IG_MA006_UNGROUPED_9336" ItemGroupRepeatKey="1" TransactionType="Insert">'
    
    # section a
    _screening_date = data_odk['GENERAL_INFORMATION_SCREENING_D'].strftime('%Y-%m-%d')
    _odm_data = _odm_data + write_odm_line('I_MA006_SCREENING_D', data_odk['GENERAL_INFORMATION_SCREENING_D'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_ENROL_S', data_odk['GENERAL_INFORMATION_ENROL_S'])
    # section b
    _odm_data = _odm_data + write_odm_line('I_MA006_ENROL_INIT', data_odk['GENERAL_INFORMATION_ENROL_INIT'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PREGNT_CONF', data_odk['ELIGIBILTY_CRITERIA_PREGNT_CONF'])
    _odm_data = _odm_data + write_odm_line('I_MA006_RES_1Y_SITE', data_odk['ELIGIBILTY_CRITERIA_RES_1_Y_SITE'])
    _odm_data = _odm_data + write_odm_line('I_MA006_AGE_16', data_odk['ELIGIBILTY_CRITERIA_AGE_16'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_3M_ABS', data_odk['ELIGIBILTY_CRITERIA_MAL_HX_3_M_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_TX_HX_ANTIMAL_3M_ABS', data_odk['ELIGIBILTY_CRITERIA_TX_HX_ANTIMAL_3_M_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_FP_WILLING', data_odk['ELIGIBILTY_CRITERIA_FP_WILLING'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_SEVERE_ABS', data_odk['ELIGIBILTY_CRITERIA_MAL_HX_SEVERE_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_BREATH_ISSUE_ABS', data_odk['ELIGIBILTY_CRITERIA_CHRON_CNS_SYMPT_ABS_BREATH_ISSUE_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_CHEST_BELLY_PAIN_ABS', data_odk['ELIGIBILTY_CRITERIA_CHRON_CNS_SYMPT_ABS_CHEST_BELLY_PAIN_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_DIZZINESS_ABS', data_odk['ELIGIBILTY_CRITERIA_CHRON_CNS_SYMPT_ABS_DIZZINESS_ABS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_CONFUSION_ABS', data_odk['ELIGIBILTY_CRITERIA_CHRON_CNS_SYMPT_ABS_CONFUSION_ABS'])   
    _odm_data = _odm_data + write_odm_line('I_MA006_SEVERE_VOMITING_ABS', data_odk['ELIGIBILTY_CRITERIA_CHRON_CNS_SYMPT_ABS_SEVERE_VOMITING_ABS'])
    # section c
    _odm_data = _odm_data + write_odm_line('I_MA006_INFORMED_CONSENT', data_odk['INFORMED_CONSENT_INFORMED_CONSENT'])
    # section d
    _odm_data = _odm_data + write_odm_line('I_MA006_ENROL_D', data_odk['ENROLMENT_DETAILS_ENROL_D'], is_date=True)
    # section e
    _odm_data = _odm_data + write_odm_line('I_MA006_DOB', data_odk['SOCIODEMOGRAPHIC_DATA_DOB'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_DOB_UK', data_odk['SOCIODEMOGRAPHIC_DATA_DOB_UK'])
    _odm_data = _odm_data + write_odm_line('I_MA006_AGE', data_odk['SOCIODEMOGRAPHIC_DATA_AGE'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_MARITAL_STATUS', data_odk['SOCIODEMOGRAPHIC_DATA_MARITAL_STATUS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_BED_NET', data_odk['SOCIODEMOGRAPHIC_DATA_BED_NET'])
    # section f
    _odm_data = _odm_data + write_odm_line('I_MA006_ILL_3D', data_odk['MED_HISTO_CONCO_MED_ILL_3_D'])
    _odm_data = _odm_data + write_odm_line('I_MA006_FEVER', data_odk['MED_HISTO_CONCO_MED_FEVER'])
    _odm_data = _odm_data + write_odm_line('I_MA006_DIARRHEA', data_odk['MED_HISTO_CONCO_MED_DIARRHEA'])
    _odm_data = _odm_data + write_odm_line('I_MA006_COUGH', data_odk['MED_HISTO_CONCO_MED_COUGH'])
    _odm_data = _odm_data + write_odm_line('I_MA006_VOMITING', data_odk['MED_HISTO_CONCO_MED_VOMITING'])
    _odm_data = _odm_data + write_odm_line('I_MA006_RASH', data_odk['MED_HISTO_CONCO_MED_RASH'])
    _odm_data = _odm_data + write_odm_line('I_MA006_DYSURIA', data_odk['MED_HISTO_CONCO_MED_DYSURIA'])
    _odm_data = _odm_data + write_odm_line('I_MA006_CONJ_RED', data_odk['MED_HISTO_CONCO_MED_CONJ_RED'])
    _odm_data = _odm_data + write_odm_line('I_MA006_ABDO_PAIN', data_odk['MED_HISTO_CONCO_MED_ABDO_PAIN'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX', data_odk['MED_HISTO_CONCO_MED_MAL_HX'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_D', data_odk['MED_HISTO_CONCO_MED_MAL_HX_D'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_DX', data_odk['MED_HISTO_CONCO_MED_MAL_HX_DX'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_TX', data_odk['MED_HISTO_CONCO_MED_MAL_HX_TX'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_HX_TX_OT', data_odk['MED_HISTO_CONCO_MED_MAL_HX_TX_OT'], is_utf8=True)
    # the next line is an exception, because this is a group of check-boxes; we will use a placeholder here and replace that later
    _odm_data = _odm_data + write_odm_line('I_MA006_OTHER_DISEASE_HX', '{OTHER_DISEASE_HX}')
    _odm_data = _odm_data + write_odm_line('I_MA006_OTHER_DISEASE_HX_OT', data_odk['MED_HISTO_CONCO_MED_OTHER_DISEASE_HX_OT'], is_utf8=True)
    # section g
    _odm_data = _odm_data + write_odm_line('I_MA006_MENST_1ST_DAY', data_odk['OBSETRIC_INFO_EXAM_MENST_1_ST_DAY'], is_date=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_MENST_1ST_DAY_UNKNOWN', data_odk['OBSETRIC_INFO_EXAM_MENST_1_ST_DAY_UNKNOWN'])
    _odm_data = _odm_data + write_odm_line('I_MA006_GEST_AGE', data_odk['OBSETRIC_INFO_EXAM_GEST_AGE'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_FUNDAL_HEIGHT', data_odk['OBSETRIC_INFO_EXAM_FUNDAL_HEIGHT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_WEIGHT', data_odk['OBSETRIC_INFO_EXAM_WEIGHT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_HEIGHT', data_odk['OBSETRIC_INFO_EXAM_HEIGHT'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_UPPER_ARM_CIRC', data_odk['OBSETRIC_INFO_EXAM_UPPER_ARM_CIRC'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_PREGNT_N', data_odk['OBSETRIC_INFO_EXAM_PREGNT_N'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_PREGNT_MISCA', data_odk['OBSETRIC_INFO_EXAM_PREGNT_MISCA'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PREGNT_N_MISCA', data_odk['OBSETRIC_INFO_EXAM_PREGNT_N_MISCA'], is_numeric=True)
    # section h
    _odm_data = _odm_data + write_odm_line('I_MA006_HAEMO_MEASURE', data_odk['FP_BLOOD_COL_HAEMO_MEASURE'], is_numeric=True)
    _odm_data = _odm_data + write_odm_line('I_MA006_HAEMO_MEASURE_NOT_DONE', data_odk['FP_BLOOD_COL_HAEMO_MEASURE_NOT_DONE'])
    _odm_data = _odm_data + write_odm_line('I_MA006_HAEMO_MEASURE_NOT_DONE_OT', data_odk['FP_BLOOD_COL_HAEMO_MEASURE_NOT_DONE_OT'])
    _odm_data = _odm_data + write_odm_line('I_MA006_FP_BLOOD_COL', data_odk['FP_BLOOD_COL_FP_BLOOD_COL'])
    _odm_data = _odm_data + write_odm_line('I_MA006_FP_BLOOD_COL_T', data_odk['FP_BLOOD_COL_FP_BLOOD_COL_T'], is_time=True)
    # section i
    _odm_data = _odm_data + write_odm_line('I_MA006_LAMP_BLOOD_ALIQUOTED', data_odk['SAMP_MAN_RDT_MICRO_LAMP_BLOOD_ALIQUOTED'])
    _odm_data = _odm_data + write_odm_line('I_MA006_SLIDES_2_PREP', data_odk['SAMP_MAN_RDT_MICRO_SLIDES_2_PREP'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MICROTAINER_COL', data_odk['SAMP_MAN_RDT_MICRO_MICROTAINER_COL'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_DONE', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_DONE'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_VAL', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_VAL'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_HRP2', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_HRP2'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_PLDH', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_PLDH'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_POS', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_POS'])
    _odm_data = _odm_data + write_odm_line('I_MA006_MAL_RDT_T', data_odk['SAMP_MAN_RDT_MICRO_MAL_RDT_T'], is_time=True)
    # section j
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_RES_COM', data_odk['PAT_MANA_PM_RES_COM'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_RES_COM_WHY', data_odk['PAT_MANA_PM_RES_COM_WHY'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_RES_COM_WHY_OT', data_odk['PAT_MANA_PM_RES_COM_WHY_OT'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_ANTIMAL_TX', data_odk['PAT_MANA_PM_ANTIMAL_TX'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_ANTIMAL_TX_WHY', data_odk['PAT_MANA_PM_ANTIMAL_TX_WHY'])
    _odm_data = _odm_data + write_odm_line('I_MA006_PM_ANTIMAL_TX_WHY_OT', data_odk['PAT_MANA_PM_ANTIMAL_TX_WHY_OT'])
    # section k
    _odm_data = _odm_data + write_odm_line('I_MA006_RECO_PREV', data_odk['PAT_RECO_RECO_PREV'])
    _odm_data = _odm_data + write_odm_line('I_MA006_RECO_COUNS_SYMPT', data_odk['PAT_RECO_RECO_COUNS_SYMPT'])
    _odm_data = _odm_data + write_odm_line('I_MA006_RECO_T', data_odk['PAT_RECO_RECO_T'], is_time=True)    
    # section k
    _odm_data = _odm_data + write_odm_line('I_MA006_SCREEN_ELI_COMMENTS', data_odk['COMMENTS_SCREEN_ELI_COMMENTS'], is_utf8=True)

    # closing it all
    _odm_data = _odm_data + '          </ItemGroupData>'
    _odm_data = _odm_data + '        </FormData>'
    _odm_data = _odm_data + '      </StudyEventData>'
    _odm_data = _odm_data + '    </SubjectData>'
    _odm_data = _odm_data + '  </ClinicalData>'
    _odm_data = _odm_data + '</ODM>'

    return _odm_data
