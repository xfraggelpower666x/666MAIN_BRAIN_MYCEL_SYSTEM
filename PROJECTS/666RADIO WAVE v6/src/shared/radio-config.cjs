'use strict';
module.exports=Object.freeze({
  radioBase:'https://webradio.666soundsdesign-broadcaster.com',
  stream:'/stream',fallbackStream:'/fallback-stream',nowPlaying:'/api/nowplaying',
  loginRoute:'/api/admin/login',gateRoute:'/api/admin/gate-check',skipRoute:'/api/admin/skip',
  adminConfigCurrentRoute:'/api/admin/config/current',adminConfigBackupsRoute:'/api/admin/config/backups',
  adminConfigUpdateRoute:'/api/admin/config/update',adminConfigRollbackRoute:'/api/admin/config/rollback',
  discordMessageRoute:'/api/discord/message',discordManualRoute:'/api/discord/manual',discordNowPlayingRoute:'/api/discord/nowplaying',
  playerAlertSendRoute:'/api/player-alert/send',playerAlertCurrentRoute:'/api/player-alert/current',playerAlertHistoryRoute:'/api/player-alert/history',playerAlertStatusRoute:'/api/player-alert/status',
  requestTimeoutMs:15000,messageMax:1800,playerAlertMax:240
});
