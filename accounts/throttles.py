from rest_framework.throttling import UserRateThrottle


class OTPThrottle(UserRateThrottle):
    rate = "5/min"
