from abc import ABC, abstractmethod
from fastapi import FastAPI


class AppModule(ABC):
    """Abstract base class for application modules.
    
    Each module should inherit from this class and implement the init method
    to configure the FastAPI application with its specific routes, dependencies,
    and middleware.
    
    Optional lifecycle methods on_startup and on_shutdown can be overridden
    to handle module-specific startup and shutdown logic.
    """
    
    @abstractmethod
    def init(self, app: FastAPI) -> None:
        """Initialize the module by configuring the FastAPI application.
        
        Args:
            app: The FastAPI application instance to configure
        """
        pass
    
    async def on_startup(self) -> None:
        """Optional startup logic for the module.
        
        This method is called during the FastAPI lifespan startup phase.
        Override this method to implement module-specific startup logic.
        """
        pass
    
    async def on_shutdown(self) -> None:
        """Optional shutdown logic for the module.
        
        This method is called during the FastAPI lifespan shutdown phase.
        Override this method to implement module-specific cleanup logic.
        """
        pass