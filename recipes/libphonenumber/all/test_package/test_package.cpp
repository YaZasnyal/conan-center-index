#include <cstdlib>
#include <iostream>

#include <phonenumbers/phonenumberutil.h>

int main()
{
    using i18n::phonenumbers::PhoneNumberUtil;
    const PhoneNumberUtil* const phone_util = PhoneNumberUtil::GetInstance();
    (void*)phone_util;

    std::cout << "Compiled with libphonenumber\n";
    return EXIT_SUCCESS;
}
