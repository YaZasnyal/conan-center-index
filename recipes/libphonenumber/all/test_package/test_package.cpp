#include <cstdlib>
#include <iostream>

#include <phonenumbers/phonenumberutil.h>
#ifdef WITH_GEOCODER
#include <phonenumbers/geocoding/phonenumber_offline_geocoder.h>
#endif

int main()
{
    /// Test libphonenumber
    using i18n::phonenumbers::PhoneNumberUtil;
    const PhoneNumberUtil* const phone_util = PhoneNumberUtil::GetInstance();
    i18n::phonenumbers::PhoneNumber number;
    phone_util->Parse("+71234567890", "RU", &number);

#ifdef WITH_GEOCODER
    /// Test libgeocoding
    i18n::phonenumbers::PhoneNumberOfflineGeocoder geocoder;
    geocoder.GetDescriptionForNumber(number, "ru-RU", "RU");
#endif

    std::cout << "Compiled with libphonenumber\n";
    return EXIT_SUCCESS;
}
