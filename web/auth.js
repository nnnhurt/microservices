const kc = new Keycloak({
   url: "https://id.klsh.ru",
   realm: "sirius",
   clientId: "sirius-frontend"
})

const authInit = async () =>
{
   try
   {
      const authenticated = await kc.init();
      if (authenticated)
      {
         console.log('User is authenticated');
      } else
      {
         console.log('User is not authenticated');
      }
   } catch (error)
   {
      console.error('Failed to initialize adapter:', error);
   }
}

authInit()
