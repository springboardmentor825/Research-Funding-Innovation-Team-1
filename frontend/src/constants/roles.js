export const ROLES = {
  RESEARCHER: 'researcher',
  STARTUP_FOUNDER: 'startup_founder',
  ADMINISTRATOR: 'administrator',
}

export const PUBLIC_ROLES = [
  { value: ROLES.RESEARCHER, label: 'Researcher' },
  { value: ROLES.STARTUP_FOUNDER, label: 'Startup Founder' },
]

export const ALL_LOGIN_ROLES = [
  ...PUBLIC_ROLES,
  { value: ROLES.ADMINISTRATOR, label: 'Administrator' },
]
