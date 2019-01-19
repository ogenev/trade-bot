

magicNumber = 1234
lots = 0.1
MAFastPeriod = 10
MAMediumPeriod = 25
MASlowPeriod = 50

slippage = 3
takeProfit = 0
stopLoss = 0
ticket: int
counter: int
openOrder: bool
buySignal: bool
sellSignal: bool

//+------------------------------------------------------------------+
//| expert initialization function                                   |
//+------------------------------------------------------------------+
int init()
{
   return(0);
}
//+------------------------------------------------------------------+
//| expert deinitialization function                                 |
//+------------------------------------------------------------------+
int deinit()
{
   return(0);
}
//+------------------------------------------------------------------+
//| expert start function                                            |
//+------------------------------------------------------------------+
def start():
    openOrder = false
    generateSignals()
   
   # monitor open trades
   for(counter=0;counter<OrdersTotal();counter++)   
   {
      OrderSelect(counter, SELECT_BY_POS, MODE_TRADES);     
      if (OrderMagicNumber() == magicNumber)
      {
         openOrder = true;
         if (OrderType() == OP_BUY && !buySignal)
         {
            closeBuyTrade();
            openOrder = false;
         }
         elif (OrderType() == OP_SELL && !sellSignal)
         {
            closeSellTrade();
            openOrder = false;
         }
      }
   }
   
   # if there are no open orders, check for a signal
   if (!openOrder)
   {
      if (buySignal)
         placeBuy();
      else if (sellSignal)
         placeSell();
   }   
   return(0);
}
//+------------------------------------------------------------------+
//| place BUY trade                                                  |
//+------------------------------------------------------------------+
void placeBuy()
{
   RefreshRates();            
   ticket=OrderSend(Symbol(),OP_BUY,lots,Ask,slippage,stopLoss,takeProfit,"buy",magicNumber,0,Green);  
   if(ticket<0)
   {
      Print("BUY failed with error #",GetLastError()," at ",Ask);
      return;
   }
}
//+------------------------------------------------------------------+
//| place SELL trade                                                 |
//+------------------------------------------------------------------+
void placeSell()
{
   RefreshRates();            
   ticket=OrderSend(Symbol(),OP_SELL,lots,Bid,slippage,stopLoss,takeProfit,"sell",magicNumber,0,Red);  
   if(ticket<0)
   {
      Print("SELL failed with error #",GetLastError()," at ",Bid);
      return;
   }
}
//+------------------------------------------------------------------+
//| generate a buy or sell signal
//+------------------------------------------------------------------+
void generateSignals()
{
   buySignal = false;
   sellSignal = false;
   
   if (iMA(NULL,0,MAFastPeriod,0,MODE_EMA,PRICE_CLOSE,1) > iMA(NULL,0,MAMediumPeriod,0,MODE_EMA,PRICE_CLOSE,1) &&
       iMA(NULL,0,MAMediumPeriod,0,MODE_EMA,PRICE_CLOSE,1) > iMA(NULL,0,MASlowPeriod,0,MODE_EMA,PRICE_CLOSE,1))
      buySignal = true;

   if (iMA(NULL,0,MAFastPeriod,0,MODE_EMA,PRICE_CLOSE,1) < iMA(NULL,0,MAMediumPeriod,0,MODE_EMA,PRICE_CLOSE,1) &&
       iMA(NULL,0,MAMediumPeriod,0,MODE_EMA,PRICE_CLOSE,1) < iMA(NULL,0,MASlowPeriod,0,MODE_EMA,PRICE_CLOSE,1))
      sellSignal = true;
}
//+------------------------------------------------------------------+
//| close BUY trade
//+------------------------------------------------------------------+
void closeBuyTrade()
{
      RefreshRates();
      OrderClose(OrderTicket(),OrderLots(),Bid,slippage,Green);     
}
//+------------------------------------------------------------------+
//| close SELL trade
//+------------------------------------------------------------------+
void closeSellTrade()
{
      RefreshRates();
      OrderClose(OrderTicket(),OrderLots(),Ask,slippage,Red);  
}